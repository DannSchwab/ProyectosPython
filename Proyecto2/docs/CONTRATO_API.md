# Contrato de la API

> **Actualizado el 28 de octubre** con lo que hace de verdad la API que programó Argail (versión del 25/10). Es la referencia para la interfaz (T5) y las pruebas (T6). Cualquier cambio se habla con el jefe.

Un **contrato** es el acuerdo sobre qué se envía y qué se recibe exactamente. Sirve para que varias personas programen piezas que tienen que encajar.

- 📌 = lo exige el enunciado.
- ⏳ = pendiente de arreglar antes del **jueves 29 por la noche**.

---

## Dirección y arranque

- `http://127.0.0.1:8000`, arrancando desde la carpeta `Proyecto2/` con `uvicorn api.main:app --reload`.
- 📌 Importa `cargar_lineas` y `construir_features` de `logtools.py`, sin copiar su código.
- 📌 El modelo se carga **una sola vez, al arrancar**. Por defecto lee `modelo.joblib` de `Proyecto2/`; con la variable de entorno `MODELO_PATH` se puede usar otro fichero.
- Si falta el modelo, la API arranca igualmente, pero `/salud` y `/analizar` responden **503** con un mensaje que explica cómo generarlo.

---

## `GET /salud`

Respuesta 200 (comprobada):

```json
{
  "estado": "ok",
  "modelo_cargado": true,
  "caracteristicas_esperadas": ["n_eventos", "n_fallos", "n_ok", "n_usuarios", "n_inv",
                                "duracion_min", "ratio_fallos", "fallos_por_min",
                                "es_interna", "max_fallos_5min", "hora_media"],
  "limite_lineas": 50000
}
```

La lista de características se saca del propio modelo (`modelo.feature_names_in_`), no está escrita a mano.

---

## `POST /analizar`

### Petición

| Campo | Tipo | ¿Obligatorio? | Por defecto | Regla |
|---|---|---|---|---|
| `lineas` | lista de textos | 📌 sí | — | Entre 1 y 50 000 líneas |
| `umbral` | número | no | 📌 `0.7` | 📌 Entre 0 y 1 |
| `lista_blanca` | lista de IPs | no | `[]` | Tienen que ser IPs válidas. 📌 Nunca aparecen como sospechosas |

No se admiten campos extra: cualquier otro campo da 422.

**¿Por qué 50 000 líneas como máximo?** Con la semilla 21, el `auth.log` completo tiene 12 425 líneas. 50 000 deja margen para analizar un log entero y a la vez impide que alguien tumbe el servicio enviando millones de líneas.

### Respuesta correcta (código 200)

| Campo | Tipo | Significado |
|---|---|---|
| `lineas_ignoradas` | entero | 📌 Líneas que no tienen el formato de `auth.log` |
| `ips_analizadas` | entero | 📌 IPs distintas analizadas, **sin contar las de la lista blanca** |
| `sospechosas` | lista | 📌 IPs con probabilidad ≥ umbral que no están en la lista blanca. Vienen **ordenadas por IP**, no por probabilidad: si se quieren de mayor a menor, que las ordene la interfaz |
| `sospechosas[].ip` | texto | 📌 |
| `sospechosas[].probabilidad` | número entre 0 y 1 | 📌 Redondeado a 4 decimales |
| `sospechosas[].motivo` | texto | 📌 Por qué se marca, en lenguaje humano (lo redacta `api/motivos.py`) |

Se usa **≥** (mayor o igual), el mismo criterio que usa el cuaderno en `evaluar_xy`.

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

---

## Errores

📌 Los errores usan códigos HTTP adecuados (422 para datos inválidos) y mensajes comprensibles. Nunca debe salir un **500**: si sale, es un fallo nuestro.

| Situación | Código | Forma de `detail` |
|---|---|---|
| JSON mal formado, falta `lineas`, tipo incorrecto o campo extra | 422 | Lista de textos |
| `umbral` menor que 0 o mayor que 1 | 422 | Lista de textos |
| `lineas` vacía o con más de 50 000 | 422 | Lista de textos |
| IP no válida en `lista_blanca` | 422 | Lista de textos |
| Ninguna línea reconocible | 422 | Texto |
| Falta el modelo | 503 | Texto |
| ⏳ Línea "casi válida" (mes que no existe, hora 25, IP mal formada) | Hoy da **500**. Tras el arreglo, se contará como ignorada | — |

**La interfaz tiene que saber mostrar las dos formas de `detail`** (comprobado):

- Errores de validación: una **lista de textos**, cada uno con dónde está el problema y qué pasa. Por ejemplo: `["body → umbral: Input should be less than or equal to 1"]`.
- Errores propios de la API: un **texto**. Por ejemplo: `"No se ha reconocido ninguna línea válida de auth.log. Comprueba el formato del log."`.

---

## Trampas conocidas del kit

Como `logtools.py` **no se modifica**, la API tiene que protegerse antes de llamarlo:

1. **Log sin ninguna línea válida.** `construir_features` falla con una tabla vacía. Resuelto: la API lo comprueba antes y devuelve 422.
2. ⏳ **Líneas "casi válidas".** Con un mes que no existe (`Foo  7 10:15:32 ...`), una hora `25:15:32`, un día `Feb 31` o una IP mal formada (`from 999.1.1 port ...`), `logtools.py` lanza una excepción en vez de ignorar la línea, y la API responde 500.
   **Arreglo (Argail):** antes de llamar a `cargar_lineas`, recorrer las líneas y probar cada una con `parsear_linea` (de `logtools`) y con `ipaddress.ip_address` sobre su IP, dentro de un `try/except (KeyError, ValueError)`. Las que fallen se cuentan como ignoradas y no se pasan a `cargar_lineas`. Probado en una copia: funciona y tarda unos 0,1 segundos más con un log completo. Para probarlo: `pruebas/peticiones/extra_linea_casi_valida.json`.
3. **Orden de las columnas.** El modelo espera las características en el mismo orden que en el entrenamiento. Resuelto: la API las ordena con `modelo.feature_names_in_`.
4. **`n_inv` cuenta líneas, no intentos.** Cada intento con un usuario inexistente genera dos líneas (`Invalid user ...` y `Failed password for invalid user ...`). Resuelto en `motivos.py`, que divide entre 2.

---

## El campo `motivo` (T6, `api/motivos.py`)

La API llama a `explicar_motivo(fila)`, donde `fila` es la fila de la IP en la tabla de `construir_features`. Reglas que aplica:

| Condición | Texto |
|---|---|
| `n_usuarios` ≥ 3 | "prueba N usuarios distintos" |
| `n_inv` ≥ 1 | "presenta usuarios inexistentes (aproximadamente N intentos)", con N = `n_inv` / 2 |
| `max_fallos_5min` ≥ 5 | "N fallos en 5 minutos" |
| `n_ok` ≥ 1 y `n_fallos` ≥ 3 | "consigue entrar después de N fallos" |
| Ninguna de las anteriores | "comportamiento parecido a los ataques vistos en el entrenamiento" |

Si se cumplen varias, se juntan separadas por "; ".

- ⏳ **Jorge:** añadir una regla para los ataques lentos contra un solo usuario (`n_usuarios` = 1, muchos fallos y ningún acceso correcto), que ahora salen con el motivo genérico.
- ⏳ **Argail:** quitar de `main.py` el motivo de reserva (`_explicar_motivo` con reglas propias). Ya se usa el de Jorge, y la rúbrica pide código sin duplicar.

---

## CORS: que la página web pueda llamar a la API

Si la página se abre con doble clic (`file://...`) o desde otro puerto (por ejemplo, Live Server), el navegador **bloquea** las llamadas a la API por seguridad. Ahora mismo pasa: la petición previa del navegador recibe un 405.

⏳ **Decisión: Argail activa `CORSMiddleware`** justo después de crear `app = FastAPI(...)`. Si se añade más tarde, da un error al arrancar.

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
```

Probado en una copia: con esto, una página abierta con doble clic o desde otro puerto puede llamar a `/analizar`, y también recibe el detalle de los errores 422. Antes de poner la API en Internet, `allow_origins` debería limitarse a la dirección de la interfaz (pregunta 8 de la defensa).

---

## Lo que la API no hace

📌 La API **no bloquea** ninguna IP: solo informa. La decisión final es de una persona.
