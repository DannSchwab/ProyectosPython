# Interfaz del detector

**T5 Interfaz** · Autor: Alejandro

> Explica con tus palabras qué has hecho y por qué. El jefe tiene que poder entenderlo y defenderlo sin haberlo programado.
> La interfaz **llama a la API**: no carga el modelo directamente. Formato de las respuestas y los errores: [`../docs/CONTRATO_API.md`](../docs/CONTRATO_API.md).

## Tipo de interfaz

Página web responsive (HTML + JavaScript con `fetch`), que se vea bien en el ordenador y en el móvil *(a confirmar con Alejandro)*.

- **CORS:** si la página se abre con doble clic, el navegador bloquea las llamadas a la API. Ver el apartado "CORS" de [`../docs/CONTRATO_API.md`](../docs/CONTRATO_API.md) y decidirlo con Argail (T4).
- **Probarla como en un móvil:** usa el modo de dispositivo de las herramientas de desarrollo del navegador (F12). Desde un móvil de verdad no funcionaría tal cual: `127.0.0.1` apunta al propio móvil, no al ordenador donde está la API.

## Cómo se abre y se usa

1. Arranca la API (ver `../api/README.md`).
2. *...*

## Qué hace cada parte del código

*Carga del fichero o líneas pegadas, umbral y lista blanca, llamada a la API, tabla de resultados, mensajes de error.*

## Decisiones y por qué

*Por ejemplo: cómo se muestran los dos formatos de error de la API, qué se ve mientras se espera la respuesta.*

## Para la defensa

### Pregunta 7. ¿Qué datos personales hay en los logs y qué obligaciones implica tratarlos?
