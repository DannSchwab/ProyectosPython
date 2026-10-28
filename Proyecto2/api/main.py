"""API REST del detector de intrusiones del Proyecto DAM.

Ejecutar desde la raíz de Proyecto2:
    uvicorn api.main:app --reload

El modelo se carga una sola vez durante la importación del módulo.
"""
from __future__ import annotations

import ipaddress
import os
from pathlib import Path
from typing import Any

import joblib
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field, field_validator

from logtools import cargar_lineas, construir_features, parsear_linea
from api.motivos import explicar_motivo

# Se espera ejecutar Uvicorn desde Proyecto2/, tal como define el README del grupo.
RUTA_MODELO = Path(os.environ.get("MODELO_PATH", "modelo.joblib"))

app = FastAPI(
    title="Detector de intrusiones SSH",
    description="Analiza líneas de auth.log y devuelve IPs potencialmente sospechosas. No bloquea conexiones.",
    version="1.0.0",
)

# CORS permite que la interfaz web local pueda llamar a la API.
# Antes de desplegar en Internet, restringir allow_origins al origen real de la interfaz.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# La carga se hace una sola vez, al arrancar/importar la aplicación.
try:
    modelo = joblib.load(RUTA_MODELO)
except FileNotFoundError:
    modelo = None
    _error_carga_modelo = (
        f"No se encuentra el modelo en '{RUTA_MODELO}'. "
        "Genera auth.log y etiquetas.csv y ejecuta entrenar.py antes de arrancar la API."
    )
except Exception as exc:
    modelo = None
    _error_carga_modelo = (
        f"No se pudo cargar el modelo '{RUTA_MODELO}': {type(exc).__name__}: {exc}. "
        "Vuelve a entrenarlo con la versión de scikit-learn instalada."
    )
else:
    _error_carga_modelo = ""


class PeticionAnalizar(BaseModel):
    """Formato validado de entrada para POST /analizar."""
    model_config = ConfigDict(extra="forbid")

    lineas: list[str] = Field(..., description="Líneas de auth.log", max_length=50000)
    umbral: float = Field(default=0.7, ge=0.0, le=1.0)
    lista_blanca: list[str] = Field(default_factory=list)

    @field_validator("lineas")
    @classmethod
    def comprobar_lineas_no_vacias(cls, value: list[str]) -> list[str]:
        if not value:
            raise ValueError("'lineas' debe contener al menos una línea.")
        return value

    @field_validator("lista_blanca")
    @classmethod
    def comprobar_ips_lista_blanca(cls, value: list[str]) -> list[str]:
        normalizadas = []
        for ip in value:
            try:
                normalizadas.append(str(ipaddress.ip_address(ip.strip())))
            except ValueError as exc:
                raise ValueError(f"'{ip}' no es una dirección IP válida en 'lista_blanca'.") from exc
        return normalizadas


@app.exception_handler(RequestValidationError)
async def error_validacion(request, exc: RequestValidationError):
    """Devuelve siempre un 422 legible para errores de formato/validación."""
    detalles = []
    for error in exc.errors():
        ubicacion = " → ".join(str(parte) for parte in error.get("loc", ()))
        detalles.append(f"{ubicacion}: {error.get('msg', 'dato inválido')}")
    return JSONResponse(status_code=422, content={"detail": detalles})


def _comprobar_modelo() -> None:
    if modelo is None:
        raise HTTPException(status_code=503, detail=_error_carga_modelo)


@app.get("/salud")
def salud() -> dict[str, Any]:
    """Estado del servicio y características esperadas por el modelo."""
    _comprobar_modelo()
    caracteristicas = list(getattr(modelo, "feature_names_in_", []))
    return {
        "estado": "ok",
        "modelo_cargado": True,
        "caracteristicas_esperadas": caracteristicas,
        "limite_lineas": 50000,
    }


@app.post("/analizar")
def analizar(peticion: PeticionAnalizar) -> dict[str, Any]:
    """Analiza líneas de log agrupándolas por IP; no ejecuta bloqueos."""
    _comprobar_modelo()

    # logtools.parsear_linea puede lanzar KeyError/ValueError para líneas
    # casi válidas (mes, fecha u hora incorrectos). Filtrarlas aquí evita 500.
    lineas_validas = []
    ignoradas_previas = 0
    for linea in peticion.lineas:
        try:
            evento = parsear_linea(linea.rstrip("\n"))
            if evento is None:
                ignoradas_previas += 1
                continue
            ipaddress.ip_address(evento["ip"])
            lineas_validas.append(linea)
        except (KeyError, ValueError):
            ignoradas_previas += 1

    eventos, ignoradas_logtools = cargar_lineas(lineas_validas)
    ignoradas = ignoradas_previas + ignoradas_logtools
    if eventos.empty:
        raise HTTPException(
            status_code=422,
            detail="No se ha reconocido ninguna línea válida de auth.log. Comprueba el formato del log.",
        )

    features = construir_features(eventos)
    lista_blanca = set(peticion.lista_blanca)
    ips_analizadas = [ip for ip in features.index if ip not in lista_blanca]

    sospechosas = []
    if ips_analizadas:
        X = features.loc[ips_analizadas]
        # Reordenar/validar columnas según el modelo cuando estén disponibles.
        esperadas = list(getattr(modelo, "feature_names_in_", []))
        if esperadas:
            faltantes = [col for col in esperadas if col not in X.columns]
            if faltantes:
                raise HTTPException(
                    status_code=500,
                    detail=f"Las características calculadas no coinciden con el modelo; faltan: {faltantes}.",
                )
            X = X[esperadas]

        probabilidades = modelo.predict_proba(X)
        clases = list(getattr(modelo, "classes_", [0, 1]))
        try:
            indice_atacante = clases.index(1)
        except ValueError:
            raise HTTPException(
                status_code=500,
                detail="El modelo cargado no tiene una clase positiva (1) para identificar atacantes.",
            )

        for ip, probabilidad in zip(ips_analizadas, probabilidades[:, indice_atacante]):
            probabilidad = float(probabilidad)
            if probabilidad >= peticion.umbral:
                fila = features.loc[ip]
                sospechosas.append({
                    "ip": str(ip),
                    "probabilidad": round(probabilidad, 4),
                    "motivo": explicar_motivo(fila),
                })

    sospechosas.sort(key=lambda resultado: resultado["ip"])
    return {
        "lineas_ignoradas": int(ignoradas),
        "ips_analizadas": len(ips_analizadas),
        "sospechosas": sospechosas,
    }
