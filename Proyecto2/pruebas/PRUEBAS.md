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

También se han utilizado Postman para enviar las peticiones HTTP y comprobar las respuestas de la API.

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

**Conclusión:** la petición se procesa sin errores y la respuesta no incluye IP sospechosas. Queda pendiente contrastar con el contrato del proyecto si las IP incluidas en la lista blanca deben contabilizarse dentro de `ips_analizadas`.

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
- **Resultado esperado:** procesar la petición sin provocar un error interno; la línea no válida debe ignorarse si el comportamiento acordado con el equipo es continuar con las líneas válidas.
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
Postman o cliente HTTP
        |
        v
API (FastAPI): recibe y valida el JSON
        |
        v
Procesamiento de logs y extracción de características
        |
        v
Modelo de IA (modelo.joblib): estima el comportamiento sospechoso
        |
        v
explicar_motivo(): genera una explicación legible
        |
        v
Respuesta JSON: líneas ignoradas, IP analizadas e IP sospechosas
```

La API permite enviar una petición mediante Postman o desde la documentación interactiva de FastAPI en `/docs`. Tras validar la entrada, procesa las líneas del log, extrae características, utiliza el modelo entrenado y devuelve los resultados en JSON.

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

**¿Qué pasaría si el director bloquea una IP por error?**

El sistema podría dejar sin servicio a un usuario legítimo. El modelo puede producir falsos positivos, por lo que no conviene bloquear automáticamente una IP solo porque aparezca como sospechosa. La API debe servir como apoyo para la decisión: una persona responsable revisa la probabilidad, los motivos y los registros antes de actuar. También conviene registrar las decisiones y disponer de un procedimiento para retirar el bloqueo si se confirma que fue un error.
