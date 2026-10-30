# Interfaz Gráfica - Detector de Intrusiones SSH (T5)

Esta carpeta contiene la interfaz web desarrollada para interactuar de forma visual con la API del detector de intrusiones del Proyecto 2 (Optativa Python para IA, 2º DAM).

## Tecnologías utilizadas
* **HTML5**: Estructura semántica de la página y formulario de entrada.
* **CSS3**: Estilos visuales adaptados con diseño *responsive* (compatible con ordenadores y dispositivos móviles mediante media queries).
* **JavaScript (Vanilla)**: Lógica de eventos, transformación de datos a formato JSON y comunicación asíncrona con la API mediante la API `fetch`.

## Estructura de ficheros
* `index.html`: Esqueleto principal de la página web. Contiene el formulario para introducir el log, el umbral, la lista blanca y las secciones dinámicas para mostrar errores o resultados.
* `styles.css`: Hoja de estilos encargada del diseño visual, la maquetación y la adaptabilidad móvil.
* `script.js`: Código encargado de capturar los datos del formulario, formatear las líneas y la lista blanca, realizar la petición `POST` a la API y pintar de forma dinámica la tabla de resultados o los errores de validación.

## Cómo usar la interfaz

1. **Arrancar la API:**
   Desde la carpeta raíz del proyecto (`Proyecto2/`), con el entorno virtual activado y el modelo ya entrenado (`modelo.joblib`):
   ```bash
   uvicorn api.main:app --reload
   ```
   La API queda en `http://127.0.0.1:8000`. Se puede comprobar abriendo `http://127.0.0.1:8000/salud` en el navegador.

2. **Abrir la interfaz:**
   Abre `interfaz/index.html` en el navegador (doble clic). No necesita servidor propio.

3. **Analizar un log:**
   * Pega las líneas de `auth.log` en el cuadro de texto, o carga un fichero `.log` / `.txt` (su contenido se copia al cuadro).
   * Ajusta el **umbral** (de 0 a 1, por defecto 0.7): solo se muestran las IPs con probabilidad igual o superior.
   * Opcionalmente, escribe una **lista blanca** de IPs separadas por comas; esas IPs no se analizan.
   * Pulsa **Analizar log**.

4. **Leer el resultado:**
   Se muestran las líneas ignoradas, las IPs analizadas y una tabla con las IPs sospechosas (IP, probabilidad y motivo). La herramienta solo informa: nunca bloquea una IP, la decisión la toma una persona.

## Cómo se comunica con la API

La interfaz envía un `POST` a `http://127.0.0.1:8000/analizar` con este JSON (formato del contrato):

```json
{
  "lineas": ["Oct  7 09:02:11 srv-web01 sshd[1840]: Failed password for ana from ..."],
  "umbral": 0.7,
  "lista_blanca": ["203.0.113.45"]
}
```

y espera esta respuesta:

```json
{
  "lineas_ignoradas": 3,
  "ips_analizadas": 384,
  "sospechosas": [
    { "ip": "203.0.113.45", "probabilidad": 0.9312, "motivo": "..." }
  ]
}
```

## Validaciones y errores

Antes de llamar a la API, la interfaz comprueba que:
* hay al menos una línea de log (se ignoran las líneas vacías y se admiten saltos de línea de Windows),
* no se supera el límite de 50 000 líneas por petición,
* el umbral es un número entre 0 y 1.

Los errores se muestran en un recuadro rojo con un mensaje comprensible:
* **422** (umbral fuera de rango, IP de la lista blanca no válida, log sin líneas reconocibles...): se muestra el campo `detail` de la API, ya sea un texto o una lista de textos.
* **503**: la API arrancó sin el modelo (falta ejecutar `entrenar.py`); se muestra el motivo que da la API.
* **Error de conexión**: la API está apagada o bloquea la llamada por CORS.

Todo texto que viene del log o de la API se escapa antes de insertarlo en la página para evitar inyección de código (XSS).

## Problemas frecuentes

* **"Error de conexión"**: comprueba que `uvicorn api.main:app` está en marcha y, si lo está, que la API tiene activado `CORSMiddleware` (el contrato exige que acepte llamadas desde cualquier página; sin él el navegador bloquea la petición aunque la API funcione).
* **Error 503**: genera el log y entrena el modelo (`generar_logs.py --seed 21` y `entrenar.py`) antes de arrancar la API.
