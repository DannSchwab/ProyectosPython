# API REST del detector

**T4 API** · Autor: Argail · `motivos.py`: Jorge (T6)

> Explica con tus palabras qué has hecho y por qué. El jefe tiene que poder entenderlo y defenderlo sin haberlo programado.
> Antes de empezar, lee [`../docs/CONTRATO_API.md`](../docs/CONTRATO_API.md), sobre todo el apartado "Trampas conocidas del kit".

## Cómo se arranca

Desde la carpeta `Proyecto2/`, con `modelo.joblib` ya generado:

```bash
uvicorn api.main:app --reload
```

## Qué hace cada parte del código

*Recorre `main.py` de arriba abajo: carga del modelo, modelo de datos de la petición, `/salud`, `/analizar`.*

## Decisiones y por qué

*Por ejemplo: cómo se valida la entrada, qué pasa con las líneas que hacen fallar a `logtools.py`, cómo se aplica la lista blanca, por qué ese límite de líneas.*

## Opcional: clave de API

Ampliación del enunciado: "Añade autenticación por clave de API y un límite de peticiones por minuto". **Solo cuando la parte obligatoria funcione** (viernes 23) y **avisando antes a T5 y T6**, porque la interfaz y las pruebas tendrán que enviar la clave.

## Para la defensa

### Pregunta 6. ¿Cómo actualizarías el modelo en producción sin parar el servicio?

### Pregunta 8. ¿Qué añadirías a la API antes de ponerla en Internet (autenticación, límites, HTTPS)?
