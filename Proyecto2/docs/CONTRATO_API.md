# Contrato de la API

> **Estado: PROPUESTA.** Se acepta antes de empezar (martes 13 de octubre). Después, cualquier cambio se habla con el jefe y con T4 (API), T5 (interfaz) y T6 (pruebas y motivos).

Un **contrato** es el acuerdo sobre qué se envía y qué se recibe exactamente. Sirve para que tres personas programen a la vez piezas que tienen que encajar sin esperar unas a otras.

En cada apartado se distingue:
- 📌 **Enunciado**: lo exige el profesor; no se negocia.
- 💡 **Propuesta**: decisión nuestra; se puede cambiar si se acuerda.

---

## Dirección y arranque

- 💡 `http://127.0.0.1:8000` (puerto por defecto de `uvicorn`).
- 💡 Se arranca desde la carpeta `Proyecto2/` con `uvicorn api.main:app --reload`. Así `api/main.py` puede hacer `import logtools` (comprobado).
- 📌 Se **importan** `cargar_lineas` y `construir_features` desde `logtools.py`; no se copia su código.
- 📌 El modelo se carga **una sola vez, al arrancar** (no en cada petición).
- 💡 Si `modelo.joblib` no existe, el servidor no arranca y muestra un mensaje claro: "Falta modelo.joblib: ejecuta entrenar.py".

---

## `GET /salud`

📌 Devuelve `{"estado": "ok"}` y la información útil que consideremos.

💡 Respuesta propuesta (código 200):

```json
{
  "estado": "ok",
  "caracteristicas": ["n_eventos", "n_fallos", "n_ok", "n_usuarios", "n_inv",
                      "duracion_min", "ratio_fallos", "fallos_por_min",
                      "es_interna", "max_fallos_5min", "hora_media"],
  "umbral_por_defecto": 0.7,
  "max_lineas": 50000
}
```

`caracteristicas` se saca del propio modelo (`modelo.feature_names_in_`), no se escribe a mano. La lista de arriba es la que tiene un modelo entrenado con el kit (comprobado).

---

## `POST /analizar`

### Petición

| Campo | Tipo | ¿Obligatorio? | Por defecto | Regla |
|---|---|---|---|---|
| `lineas` | lista de textos | 📌 sí | — | 💡 entre 1 y 50 000 líneas |
| `umbral` | número | no | 📌 `0.7` | 📌 entre 0 y 1 |
| `lista_blanca` | lista de textos (IPs) | no | 💡 `[]` | 📌 estas IPs **nunca** aparecen como sospechosas |

💡 **¿Por qué 50 000 líneas como máximo?** Un `auth.log` completo generado con el kit tiene entre 13 000 y 16 000 líneas (comprobado con 5 semillas distintas). 50 000 deja margen para analizar un log entero y a la vez impide que alguien tumbe el servicio enviando millones de líneas.

### Respuesta correcta (código 200)

| Campo | Tipo | Significado |
|---|---|---|
| `lineas_ignoradas` | entero | 📌 Líneas que no se han podido interpretar |
| `ips_analizadas` | entero | 📌 IPs distintas encontradas. 💡 Incluye las de la lista blanca: se analizan, pero nunca se marcan |
| `sospechosas` | lista | 📌 IPs con probabilidad ≥ umbral que no están en la lista blanca. 💡 Ordenadas de mayor a menor probabilidad |
| `sospechosas[].ip` | texto | 📌 |
| `sospechosas[].probabilidad` | número (0–1) | 📌 💡 Redondeado a 3 decimales |
| `sospechosas[].motivo` | texto | 📌 Por qué se marca, en lenguaje humano |

💡 Se usa **≥** (mayor o igual) porque es el mismo criterio que usa el cuaderno en `evaluar_xy`.

Forma de la respuesta (los `<...>` se sustituyen por valores reales; esto **no** es un resultado):

```text
{
  "lineas_ignoradas": <entero>,
  "ips_analizadas": <entero>,
  "sospechosas": [
    {"ip": "<ip>", "probabilidad": <número entre 0 y 1>, "motivo": "<texto>"}
  ]
}
```

**T5 (interfaz):** mientras la API no exista, crea `interfaz/respuesta_simulada.json` con esta forma y valores inventados por ti (que se note que son falsos, por ejemplo IPs `0.0.0.x`), y haz que la interfaz lo lea. Cuando la API funcione, cambias la lectura del fichero por la llamada real.

---

## Errores

📌 Los errores usan códigos HTTP adecuados (422 para datos inválidos) y mensajes comprensibles. Nunca debe salir un **500**: si sale, es un fallo nuestro.

| Situación | Código | Quién lo produce |
|---|---|---|
| JSON mal formado, falta `lineas` o un campo tiene un tipo incorrecto | 422 | FastAPI automáticamente |
| `umbral` menor que 0 o mayor que 1 | 422 | FastAPI automáticamente si se declara con `Field(ge=0, le=1)` |
| `lineas` vacía o con más de 50 000 | 422 | Validación del modelo de datos o comprobación propia |
| Ninguna línea reconocible | 422 | Comprobación propia, p. ej. "Ninguna línea tiene el formato de auth.log" |

### ⚠️ El cuerpo de los errores no siempre tiene la misma forma

Comprobado con FastAPI 0.143: todos los errores traen un campo `detail`, pero:

- en los errores **automáticos** de validación, `detail` es una **lista** de objetos (cada uno con un `msg` que explica el problema);
- en los errores **propios** (`HTTPException`), `detail` es un **texto**.

**Decisión pendiente (antes del martes 13):** o la interfaz (T5) sabe mostrar los dos casos, o la API (T4) unifica el formato. Lo más sencillo es lo primero.

---

## Trampas conocidas del kit (comprobadas)

Estas situaciones hacen que el código del kit falle. Como `logtools.py` **no se modifica**, la API tiene que protegerse antes de llamarlo:

1. **Log sin ninguna línea válida.** `construir_features` falla con una tabla vacía (`AttributeError`). Hay que comprobar antes que hay al menos un evento y devolver 422.
2. **Líneas "casi válidas".** Algunas líneas con la forma correcta pero datos imposibles no se ignoran, sino que lanzan una excepción:
   - mes que no existe (`Foo  7 10:15:32 ...`) → `KeyError` en `parsear_linea`;
   - hora `25:15:32` o día `Feb 31` → `ValueError` en `parsear_linea`;
   - IP mal formada (`from 999.1.1 port ...`) → pasa `cargar_lineas`, pero falla luego en `construir_features`.

   Tienen que acabar como ignoradas o como un 422 claro, nunca como un 500. Es un buen caso para el documento de pruebas (`pruebas/peticiones/extra_linea_casi_valida.json`).
3. **Orden de las columnas.** El modelo espera las características en el mismo orden que en el entrenamiento: seleccionarlas con `X[modelo.feature_names_in_]`.
4. **`n_inv` cuenta líneas, no intentos.** Cada intento con un usuario inexistente genera dos líneas (`Invalid user ...` y `Failed password for invalid user ...`), así que `n_inv` sale aproximadamente el doble que el número de intentos. Hay que tenerlo en cuenta al redactar el `motivo`.

---

## El campo `motivo` (T6)

💡 **Firma acordada:** T6 programa en `api/motivos.py`:

```python
def explicar_motivo(fila):
    """fila: una fila de la tabla de construir_features (una IP), con acceso fila["n_usuarios"], etc.
    Devuelve un texto en lenguaje humano."""
```

y T4 la usa así: `from api.motivos import explicar_motivo`.

💡 Reglas de partida (los números son un punto de partida, no resultados; se pueden ajustar con lo que salga en E3):

| Condición | Texto |
|---|---|
| `n_usuarios` ≥ 3 | "prueba N usuarios distintos" |
| `n_inv` ≥ 1 | "N intentos con usuarios que no existen" (recuerda: `n_inv` / 2) |
| `max_fallos_5min` ≥ 5 | "N fallos en 5 minutos" |
| `n_ok` ≥ 1 y `n_fallos` ≥ 3 | "consigue entrar después de N fallos" |
| ninguna de las anteriores | "comportamiento parecido a los ataques vistos en el entrenamiento" |

Si se cumplen varias, se juntan separadas por "; ".

---

## Si la interfaz es una página web: CORS

Si la página se abre con doble clic (`file://...`) o desde otro puerto, el navegador **bloquea** las llamadas a la API por seguridad (política CORS). Dos soluciones:

- **Opción A (más sencilla):** que FastAPI sirva también la carpeta `interfaz/` (con `StaticFiles`). Así la página y la API salen del mismo sitio y no hay bloqueo.
- **Opción B:** activar `CORSMiddleware` en la API.

Esto no afecta si la interfaz es una aplicación Java o móvil. **Decisión pendiente (antes del martes 13).**

---

## Lo que la API no hace

📌 La API **no bloquea** ninguna IP: solo informa. La decisión final es de una persona.
