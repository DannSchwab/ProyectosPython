# Documento de pruebas de la API

**Proyecto:** Detector de intrusiones con IA  
**Responsable de las pruebas:** Jorge Martín Trejo  
**Servicio probado:** API de análisis de logs  
**Dirección local:** `http://127.0.0.1:8000`

## 1. Objetivo

Comprobar que la API procesa correctamente las peticiones válidas, aplica las validaciones de entrada y gestiona las líneas de log que no cumplen el formato esperado.

Las pruebas se han ejecutado con la API iniciada localmente mediante:

```powershell
python -m uvicorn api.main:app --reload
```

También se ha utilizado Postman para enviar las peticiones HTTP y comprobar las respuestas de la API.

## 2. Resumen de resultados

| # | Prueba | Fichero de petición | Código esperado | Código obtenido | ¿Coincide? |
|---|---|---|---|---|---|
| 1 | Petición correcta | `peticiones/correcta.json` | 200 | 200 | Sí |
| 2 | Petición con lista blanca (`203.0.113.45`) | `peticiones/lista_blanca.json` | 200 | 200 | Sí |
| 3 | Umbral fuera de rango (`1.5`) | `peticiones/umbral_fuera_rango.json` | 422 | 422 | Sí |
| 4 | Líneas basura, sin ninguna línea válida | `peticiones/lineas_basura.json` | 422 | 422 | Sí |
| 5 | Línea con un mes que no existe | `peticiones/extra_linea_casi_valida.json` | 200 | 200 | Sí |

## 3. Detalle de las pruebas

### Prueba 1. Petición correcta

- **Fichero:** `peticiones/correcta.json`
- **Resultado esperado:** HTTP 200 y respuesta JSON con el resultado del análisis.
- **Resultado obtenido:** HTTP 200.

Respuesta obtenida:

```json
{
  "lineas_ignoradas": 0,
  "ips_analizadas": 3,
  "sospechosas": [
    {
      "ip": "203.0.113.45",
      "probabilidad": 0.93,
      "motivo": "prueba 8 usuarios distintos; presenta usuarios inexistentes (aproximadamente 8 intentos); 8 fallos en 5 minutos"
    }
  ]
}
```

**Conclusión:** la petición se procesa correctamente. La API analiza tres IP, no ignora líneas y devuelve una IP sospechosa con su probabilidad y una explicación legible.

### Prueba 2. Petición con lista blanca

- **Fichero:** `peticiones/lista_blanca.json`
- **Resultado esperado:** HTTP 200 y ninguna IP de la lista blanca marcada como sospechosa.
- **Resultado obtenido:** HTTP 200.

Respuesta obtenida:

```json
{
  "lineas_ignoradas": 0,
  "ips_analizadas": 2,
  "sospechosas": []
}
```

**Conclusión:** la petición se procesa sin errores y la respuesta no incluye ninguna IP sospechosa. Según el contrato del proyecto, las IP incluidas en la lista blanca no se contabilizan dentro de `ips_analizadas`. Por tanto, el resultado obtenido de dos IP analizadas es correcto.

### Prueba 3. Umbral fuera de rango

- **Fichero:** `peticiones/umbral_fuera_rango.json`
- **Dato probado:** `umbral = 1.5`
- **Resultado esperado:** HTTP 422, porque el umbral supera el máximo permitido.
- **Resultado obtenido:** HTTP 422.

Mensaje devuelto:

```json
{
  "detail": [
    "body → umbral: Input should be less than or equal to 1"
  ]
}
```

**Conclusión:** la API rechaza el valor no válido y comunica que el umbral debe ser menor o igual que `1`.

### Prueba 4. Líneas basura

- **Fichero:** `peticiones/lineas_basura.json`
- **Resultado esperado:** HTTP 422 si no se reconoce ninguna línea válida del formato de `auth.log`.
- **Resultado obtenido:** HTTP 422.

Mensaje devuelto:

```json
{
  "detail": "No se ha reconocido ninguna línea válida de auth.log. Comprueba el formato del log."
}
```

**Conclusión:** la API rechaza la petición cuando no puede reconocer ninguna línea válida y devuelve un mensaje de error.

### Prueba 5. Línea con un mes que no existe

- **Fichero:** `peticiones/extra_linea_casi_valida.json`
- **Resultado esperado:** HTTP 200, sin error interno: según el contrato, la línea con el mes inexistente se cuenta en `lineas_ignoradas` y se analiza el resto.
- **Resultado obtenido:** HTTP 200.

Respuesta obtenida:

```json
{
  "lineas_ignoradas": 1,
  "ips_analizadas": 1,
  "sospechosas": []
}
```

**Conclusión:** la API ignora una línea no válida y termina el análisis sin devolver HTTP 500. La petición se procesa correctamente.

## 4. Comprobación de `explicar_motivo()`

La función `explicar_motivo(fila)`, implementada en `api/motivos.py`, construye una explicación en lenguaje natural a partir de las características de cada IP.

- Si hay tres o más usuarios distintos, indica cuántos usuarios se han probado.
- Si `n_inv` es mayor o igual que uno, informa de los usuarios inexistentes y estima los intentos mediante `n_inv / 2`, ya que este contador representa eventos y no necesariamente intentos independientes.
- Si hay cinco o más fallos en una ventana de cinco minutos, indica el número de fallos.
- Si se produce al menos un acceso correcto y hay tres o más fallos, indica que se consigue entrar después de varios fallos.
- Si se producen cinco o más fallos contra un solo usuario y no hay accesos correctos, identifica el patrón de fallos contra el mismo usuario.
- Si no se cumple ninguna regla, utiliza un motivo general relacionado con el comportamiento observado durante el entrenamiento.

En la prueba correcta, la API devuelve una explicación que combina varios de estos indicadores.

## 5. Esquema de la integración

El flujo de la aplicación es el siguiente:

```text
Interfaz web (interfaz/index.html, en el navegador)
        |  POST /analizar con fetch: líneas del log, umbral y lista blanca (JSON)
        v
API (FastAPI, api/main.py): recibe y valida el JSON
        |
        v
logtools.py: lee las líneas y calcula 11 características por IP
        |
        v
Modelo de IA (modelo.joblib): probabilidad de que cada IP sea atacante, que se compara con el umbral
        |
        v
api/motivos.py (explicar_motivo): explica por qué se marca cada IP
        |
        v
Respuesta JSON: líneas ignoradas, IPs analizadas e IPs sospechosas
        |
        v
Interfaz web: muestra la tabla o el error; la decisión la toma una persona
```

Las mismas peticiones se pueden enviar con Postman (colección `P2_detector.postman_collection.json`) o desde la documentación interactiva de FastAPI en `/docs`, que es como se han hecho estas pruebas. La API nunca bloquea una IP: solo informa.

## 6. Colección de Postman y evidencias

Para facilitar la repetición de las pruebas, se ha creado y exportado desde Postman una colección llamada `P2_detector.postman_collection.json`.

La colección contiene las cinco peticiones utilizadas durante las pruebas. Todas utilizan el método `POST` y el endpoint:

`http://127.0.0.1:8000/analizar`

Los ficheros de las peticiones se encuentran en `pruebas/peticiones/` y la colección exportada se encuentra en `pruebas/`.

También se ha preparado la carpeta `pruebas/capturas/` para almacenar las evidencias visuales de los resultados obtenidos en Postman:

- `01_correcta.png`: petición correcta.
- `02_lista_blanca.png`: prueba de lista blanca.
- `03_umbral.png`: umbral fuera de rango.
- `04_lineas_basura.png`: petición con líneas basura.
- `05_linea_invalida.png`: línea con un mes que no existe.

Estas capturas permiten comprobar visualmente las peticiones realizadas, los códigos HTTP y las respuestas recibidas.

## 7. Conclusión

Las cinco pruebas realizadas han obtenido los códigos HTTP esperados. La API acepta las peticiones válidas, rechaza el umbral fuera de rango y las entradas que no contienen ninguna línea reconocible, y puede ignorar una línea no válida sin provocar un error interno.

La función `explicar_motivo()` complementa la predicción con razones comprensibles para que una persona pueda revisar el resultado. El detector debe utilizarse como herramienta de apoyo: una IP no debería bloquearse automáticamente solo por la predicción del modelo. Antes de tomar una medida, una persona responsable debe revisar la probabilidad, los motivos y los registros disponibles para reducir el riesgo de falsos positivos.

## 8. Pregunta de defensa

**Si el detector bloquea por error la IP del director, ¿qué ha fallado y cómo lo evitarías?**

Se ha producido un **falso positivo**, es decir, el detector ha identificado como sospechosa una IP que realmente es legítima. Esto puede ocurrir cuando el modelo interpreta incorrectamente el comportamiento de una dirección IP. Con nuestros datos se ve este tipo de error: en el experimento E1, con un umbral de 0,1 el modelo marca como sospechosa 1 IP legítima. Además, la IP 192.168.1.249, un script de monitorización mal configurado, acumula 37 fallos de contraseña y parece un ataque aunque sea legítima. Al director le podría pasar algo parecido si se equivoca varias veces de contraseña o se conecta desde una red nueva.


Para evitarlo, utilizaríamos la **lista blanca**, que existe precisamente para excluir del análisis de detección las direcciones IP de confianza, como la del director. De esta manera, aunque esa IP presente algún comportamiento que pueda parecer sospechoso, no se marcaría como atacante.

Eso sí, la lista blanca también tiene un riesgo: si el ordenador del director se viera comprometido, los ataques que salieran desde su IP no se señalarían. Por eso conviene que sea una lista corta y revisada.

Además, el sistema debería utilizarse como herramienta de apoyo y no bloquear automáticamente las direcciones IP. Antes de aplicar un bloqueo, una persona responsable tendría que revisar la alerta, la probabilidad y los motivos proporcionados por el detector.
