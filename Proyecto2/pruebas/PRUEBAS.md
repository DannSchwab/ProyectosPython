# Documento de pruebas de la API

**T6 Pruebas y motivos** · Autor: Argail

> Enunciado: documentar, con capturas o con la salida de `curl`, Postman o la página `/docs`, **al menos cuatro peticiones**: una correcta, una con lista blanca, una con umbral fuera de rango y una con líneas basura. Indicar **qué esperabas y qué obtuviste**.

**Cómo trabajar sin esperar a la API:** rellena ya la columna "Esperado" a partir de [`../docs/CONTRATO_API.md`](../docs/CONTRATO_API.md) y súbelo. Cuando la API funcione (viernes 23), ejecuta cada petición y rellena "Obtenido".

## Resumen

| # | Petición | Fichero | Código esperado | Código obtenido | ¿Coincide? |
|---|---|---|---|---|---|
| 1 | Correcta | `peticiones/correcta.json` | 200 | | |
| 2 | Con lista blanca (`203.0.113.45`) | `peticiones/lista_blanca.json` | 200 | | |
| 3 | Umbral fuera de rango (1.5) | `peticiones/umbral_fuera_rango.json` | 422 | | |
| 4 | Líneas basura | `peticiones/lineas_basura.json` | 422 | | |
| 5 | *(extra)* Línea con un mes que no existe | `peticiones/extra_linea_casi_valida.json` | *(decidir con T4: 200 contándola como ignorada, o 422)* | | |

## Detalle de cada prueba

Todos los comandos se ejecutan desde la carpeta `Proyecto2/` (en Windows, `curl.exe`).

### 1. Petición correcta

- **Comando:** `curl -X POST http://127.0.0.1:8000/analizar -H "Content-Type: application/json" -d @pruebas/peticiones/correcta.json`
- **Esperado:**
- **Obtenido:** *(pegar la salida o la captura)*
- **Conclusión:**

### 2. Con lista blanca

- **Esperado:**
- **Obtenido:**
- **Conclusión:**

### 3. Umbral fuera de rango

- **Esperado:**
- **Obtenido:**
- **Conclusión:**

### 4. Líneas basura

- **Esperado:**
- **Obtenido:**
- **Conclusión:**

---

## Cómo funciona `explicar_motivo` (`api/motivos.py`)

*Explica con tus palabras qué reglas usa y por qué.*

## Para el informe: 5. Esquema de la integración

*Qué piezas hay (interfaz, API, `logtools.py`, modelo) y cómo se comunican. Se puede dibujar con Mermaid.*

## Para la defensa

### Pregunta 8. ¿Qué añadirías a la API antes de ponerla en Internet (autenticación, límites, HTTPS)?
