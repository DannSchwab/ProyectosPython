# API del detector de intrusiones (T4 — Argail)

## Qué hace

Esta API expone el modelo de detección de intentos sospechosos en logs SSH mediante FastAPI. La API **solo informa**: no bloquea IPs ni modifica el servidor.

## Requisitos previos

1. Estar en la raíz `Proyecto2/`, donde se encuentran `logtools.py`, `entrenar.py` y `requirements.txt`.
2. Instalar las dependencias con `pip install -r requirements.txt`.
3. Generar los datos y entrenar el modelo con la semilla acordada por el grupo:

```bash
python generar_logs.py --seed NUMERO_LISTA --salida auth.log --etiquetas etiquetas.csv
python entrenar.py --log auth.log --etiquetas etiquetas.csv --salida modelo.joblib
```

Sustituye `NUMERO_LISTA` por la semilla común del grupo. Los logs, etiquetas y el modelo son archivos locales y no se deben subir al repositorio.

## Arrancar el servicio

Desde `Proyecto2/`:

```bash
uvicorn api.main:app --reload
```

Por defecto busca `modelo.joblib` en la carpeta actual. Para usar otra ruta, define la variable de entorno `MODELO_PATH`. La carga se realiza una sola vez al importar la aplicación. Si no existe un modelo válido, el servicio devuelve un error HTTP 503 al acceder a los endpoints; crea o vuelve a entrenar el modelo para solucionarlo.

- API: <http://127.0.0.1:8000>
- Documentación interactiva: <http://127.0.0.1:8000/docs>

## `GET /salud`

Comprueba que el modelo está cargado y muestra las características que espera.

Ejemplo de respuesta:

```json
{
  "estado": "ok",
  "modelo_cargado": true,
  "caracteristicas_esperadas": ["n_eventos", "n_fallos"],
  "limite_lineas": 50000
}
```

La lista de características del ejemplo es ilustrativa; la respuesta real se obtiene del modelo cargado.

## `POST /analizar`

Recibe un JSON con estos campos:

- `lineas`: lista de cadenas con líneas de `auth.log` (obligatoria; máximo 50.000).
- `umbral`: número entre `0` y `1`; si se omite, vale `0.7`.
- `lista_blanca`: lista de IPs que nunca se mostrarán como sospechosas; si se omite, queda vacía.

Ejemplo:

```json
{
  "lineas": [
    "Oct  7 10:15:30 srv-web01 sshd[2101]: Invalid user admin from 203.0.113.45 port 51234",
    "Oct  7 10:15:31 srv-web01 sshd[2102]: Failed password for invalid user admin from 203.0.113.45 port 51235 ssh2"
  ],
  "umbral": 0.7,
  "lista_blanca": []
}
```

La respuesta tiene esta estructura:

```json
{
  "lineas_ignoradas": 0,
  "ips_analizadas": 1,
  "sospechosas": [
    {
      "ip": "203.0.113.45",
      "probabilidad": 0.91,
      "motivo": "2 fallos de contraseña"
    }
  ]
}
```

Los valores del ejemplo son ilustrativos, no resultados de una ejecución real. `ips_analizadas` es el número de IPs distintas analizadas, excluyendo las de la lista blanca. La probabilidad se redondea a cuatro decimales. Solo se incluyen en `sospechosas` las IPs cuya probabilidad de la clase atacante (`1`) sea mayor o igual que el umbral.

### Validaciones y errores

Los errores de validación devuelven HTTP `422` con el campo `detail`, incluyendo JSON mal formado, campos adicionales, tipos incorrectos, umbral fuera del rango, IPs inválidas en la lista blanca, más de 50.000 líneas, lista de líneas vacía o log sin ninguna línea reconocible. Si el modelo no se ha generado o no puede cargarse, la API devuelve HTTP `503` indicando cómo corregirlo.

Una línea que no tenga el formato reconocido por `logtools.py` se cuenta como ignorada. Si el lote no contiene ningún evento reconocible, se rechaza la petición con `422`.

## Cómo se integra `motivos.py`

La API importa directamente `explicar_motivo(fila)` desde `api/motivos.py`, que corresponde a T6 (Jorge). Ese módulo debe estar presente en la carpeta `api/` durante la integración. La función recibe la fila de características de una IP y devuelve el motivo en lenguaje humano.

## Seguridad y límites

- No bloquea direcciones ni ejecuta comandos del sistema.
- La lista blanca se aplica antes de clasificar y esas IPs no se incluyen en los resultados sospechosos.
- El límite de entrada es de 50.000 líneas por petición.
- Esta versión no incorpora autenticación. Antes de exponerla fuera del equipo local se deberían añadir autenticación, HTTPS, límites de frecuencia y controles de acceso.
- CORS está configurado temporalmente con `allow_origins=["*"]` para facilitar la integración de la interfaz. En producción debe limitarse al origen concreto de la interfaz autorizada; CORS no sustituye a la autenticación.

## Pruebas manuales rápidas

Con el servicio arrancado, `GET /salud` se puede probar desde el navegador o `/docs`. Para `POST /analizar`, usa `/docs` y prueba:
1. Una petición correcta con líneas válidas: debe devolver `200`.
2. Una IP incluida en `lista_blanca`: no debe aparecer en `sospechosas`.
3. `umbral: 1.5`: debe devolver `422`.
4. `lineas: ["esto no es una línea de auth.log"]`: debe devolver `422`.
5. Una línea con mes inexistente, hora `25:15:32`, fecha imposible (`Feb 31`) o IP mal formada: se cuenta como ignorada y no debe producir `500`.
6. Una petición `OPTIONS` desde el origen de la interfaz: debe incluir las cabeceras CORS.

La documentación y las pruebas definitivas del grupo se coordinan con T6 en `pruebas/PRUEBAS.md`.


## Preguntas para la defensa

### 6. ¿Cómo actualizar el modelo sin parar el servicio?

Entrenaría una nueva versión del modelo en un fichero separado y comprobaría primero que carga correctamente y supera las pruebas. Después, el servicio podría cargar esa versión en memoria y sustituir la referencia al modelo activo de forma controlada, sin interrumpir las peticiones que estén terminando con el modelo anterior. Si la carga o las comprobaciones fallan, mantendría la versión anterior. La versión actual de esta API carga el modelo una sola vez al arrancar; para disponer de actualización en caliente habría que implementar expresamente ese mecanismo o desplegar nuevas instancias y cambiar el tráfico cuando estén listas.

### 8. ¿Qué añadir antes de poner la API en Internet?

- **Autenticación y autorización** para que solo usuarios o aplicaciones permitidos puedan acceder.
- **HTTPS** para cifrar las comunicaciones.
- **Límites de frecuencia y protección frente a abuso**, además del límite actual de 50.000 líneas por petición.
- **Control de acceso, gestión segura de secretos y configuración de producción**, sin exponer información interna en los errores.
- **Registro y monitorización** de errores y actividad, evitando guardar datos sensibles innecesarios.
- **CORS restringido**: cambiar `allow_origins=["*"]` por la dirección concreta de la interfaz web autorizada. CORS no sustituye a la autenticación ni es por sí solo una medida de control de acceso.
- **Pruebas y despliegue controlado** para validar el modelo y la API antes de dirigir tráfico real.

La API solo identifica actividad sospechosa: no debe bloquear automáticamente direcciones IP ni sustituir la revisión humana.
