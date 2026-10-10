# API REST del detector

**T4 API** · Autor: Jorge · `motivos.py`: Argail (T6)

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

## Para la defensa

### Pregunta 1. Si el detector bloquea por error la dirección del director, ¿qué ha fallado y cómo lo evitarías?

### Pregunta 6. ¿Cómo actualizarías el modelo en producción sin parar el servicio?
