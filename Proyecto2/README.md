# Proyecto P2: Auditar e integrar un detector de intrusiones con IA

Optativa Python para IA, 2º DAM.

La empresa que gestiona el servidor `srv-web01` tiene un detector de intrusiones basado en Machine Learning: lee el log de autenticación SSH y señala las IPs sospechosas. El modelo viene hecho en el kit del profesor. Nuestro trabajo es **entenderlo**, **investigar hasta dónde fiarse de él**, **convertirlo en una API REST con una interfaz** y **decidir con argumentos si se podría usar en producción**.

La API solo informa: nunca bloquea una IP. La decisión final la toma siempre una persona.

## Datos

Log de autenticación SSH **sintético** de `srv-web01`, generado con `generar_logs.py` del kit. Todo el grupo usa la misma semilla: `--seed ___` (número de lista de ______).

Con los valores por defecto del kit salen 384 IPs, de las que 100 son atacantes, y entre 13 000 y 16 000 líneas según la semilla (comprobado con 5 semillas). Las IPs públicas son de rangos reservados para documentación (RFC 5737): no pertenecen a nadie real.

Los datos y el modelo **no se suben al repositorio**: cada persona los genera en su ordenador (ver [Instalación y ejecución](#instalación-y-ejecución)).

## Reparto

| Nombre | Tarea | Qué entrega | Fichero |
|---|---|---|---|
| Jia Xi | T1 Comprender | Preguntas P1–P11 con palabras propias y ejemplos del log; diagrama del flujo con los datos que viajan en cada flecha | `notebooks/T1_comprender.ipynb`, `docs/diagrama_flujo.md` |
| Sergio | T2 Experimentos I | E1 (umbral), E2 (quitar características), E3 (regla simple) y E8 (experimento propio), con hipótesis, resultado y explicación; pregunta P12 | `notebooks/T2_umbral_y_caracteristicas.ipynb` |
| Noel | T3 Experimentos II | E4 (azar del reparto), E5 (otra semilla), E6 (pocos ataques) y E7 (sin etiquetas), con hipótesis, resultado y explicación; pregunta P13 | `notebooks/T3_azar_y_datos_nuevos.ipynb` |
| Argail | T4 API | `GET /salud` y `POST /analizar` con validación, errores, lista blanca y límite de líneas; explicación de cómo funciona. *Opcional, solo cuando todo funcione:* clave de API (ampliación del enunciado), avisando antes a T5 y T6 | `api/main.py`, `api/README.md` |
| Alejandro | T5 Interfaz | Página web responsive que llama a la API: cargar o pegar el log, umbral, lista blanca, tabla de resultados y errores comprensibles; explicación | `interfaz/`, `interfaz/README.md` |
| Jorge | T6 Pruebas y motivos | Función que redacta el `motivo` de cada IP; pruebas con Postman de al menos 4 peticiones (esperado frente a obtenido) y la colección exportada | `api/motivos.py`, `pruebas/PRUEBAS.md`, `pruebas/P2_detector.postman_collection.json` |
| Daniel (jefe) | T7 Informe y revisión final | Revisión de todo, unión de cuadernos, informe, demo y entrega | `notebooks/P2_analisis_intrusiones.ipynb`, `docs/INFORME.md` |

T4, T5 y T6 están asignadas según lo que cada uno hizo en prácticas: Argail, un sistema de login (la API también valida lo que recibe y responde con errores claros); Alejandro, páginas web y diseño responsive (la interfaz); Jorge, Postman (las pruebas).

A diferencia del Proyecto 1, aquí no numeramos a las personas como P1, P2..., porque en este proyecto **P1–P13 son las preguntas del cuaderno**.

### Informe y defensa (todos aportan)

El informe y la defensa son lo que más pesa (30 %). Cada persona escribe un borrador y prepara una pregunta:

| Nombre | Borrador del informe | Pregunta de la defensa |
|---|---|---|
| Jia Xi | 1. Qué hace el sistema | 5. Atacante con 500 IPs y pocos intentos cada una |
| Sergio | 4. Recomendación | 4. Característica que "hace trampa" |
| Noel | 3. Hasta dónde fiarse | 2. Qué enseña E4 · 3. Por qué funciona tan bien |
| Argail | — | 6. Actualizar el modelo sin parar el servicio · 8. Qué añadir a la API antes de ponerla en Internet (autenticación, límites, HTTPS) |
| Alejandro | — | 7. Datos personales en los logs |
| Jorge | 5. Esquema de la integración | 1. Bloqueo del director por error |
| Daniel | 2. Qué hemos descubierto, y unión de todo | Repaso de todas |

Cada uno lo escribe en su propio fichero: en los cuadernos, en la sección "8. Mi aportación"; T4 y T5, en el `README.md` de su carpeta; T6, en `PRUEBAS.md`. El jefe lo une en `docs/INFORME.md` y `docs/DEFENSA.md`. **Todos tenemos que poder responder cualquier pregunta**: el profesor puede preguntar a quien quiera.

## Contrato (todos seguimos esto)

| Decisión | Valor |
|---|---|
| Semilla | `--seed ___` para todos |
| Ficheros del kit | `logtools.py` y `generar_logs.py` no se modifican |
| Datos y modelo | Se generan dentro de `Proyecto2/`. Nunca se suben `auth.log`, `etiquetas*.csv` ni `modelo.joblib` |
| Cuadernos | Cada uno parte de `notebooks/plantilla.ipynb`. La celda "Base común" no se toca |
| Experimentos | Hipótesis escrita y subida antes de ejecutar. Un solo cambio cada vez |
| Respuestas | Con palabras propias, sin copiar los comentarios del código ni los apuntes |
| Cifras | Solo las obtenidas al ejecutar. Nada inventado |
| Dirección de la API | `http://127.0.0.1:8000`, arrancada con `uvicorn api.main:app` desde `Proyecto2/` |
| `POST /analizar` | Entrada: `lineas`, `umbral` (0 a 1, por defecto 0.7) y `lista_blanca`. Salida: `lineas_ignoradas`, `ips_analizadas` y `sospechosas` (cada una con `ip`, `probabilidad` y `motivo`) |
| Límite | 50 000 líneas por petición |
| Errores | Código 422 con un campo `detail` que lo explica. Nunca un 500 |
| Motivo | T6 programa `explicar_motivo(fila)` en `api/motivos.py`; T4 la llama |
| Interfaz | Página web responsive (HTML + JavaScript con `fetch`) que se vea bien también en el móvil *(a confirmar con Alejandro)* |

El detalle de la API (formatos, errores y fallos conocidos del kit) está en [`docs/CONTRATO_API.md`](docs/CONTRATO_API.md). Si hay que cambiar algo del contrato, se habla antes con el jefe.

## Cómo trabajar

1. Cada persona trabaja solo en sus ficheros (columna **Fichero**), sin tocar los de los demás.
2. Antes del martes 13 de octubre, instala el kit y comprueba que funciona (ver [Instalación y ejecución](#instalación-y-ejecución)).
3. T1, T2 y T3: empieza copiando la plantilla (`notebooks/plantilla.ipynb`) con el nombre de tu fichero. Ejecuta las secciones 0 a 5 en orden y después haz tu parte.
4. Comenta el código y explica con tus palabras qué has hecho y por qué. El jefe tiene que entenderlo para poder defenderlo.
5. Experimentos (T2 y T3): escribe las hipótesis y **sube el cuaderno antes de ejecutar**. Después ejecuta y vuelve a subirlo. GitHub guarda la fecha de cada subida, así se ve que la hipótesis iba primero.
6. Termina con un "Hallazgo": 2-3 líneas con datos concretos de tus resultados.
7. Sube tus ficheros a su carpeta con **Add file → Upload files**.
   - Sube **solo tus ficheros**: nunca `auth.log`, `etiquetas.csv`, `modelo.joblib` ni la carpeta `.venv`. Al subir por la web, el `.gitignore` no los frena.
   - Sube el cuaderno **`.ipynb`**, no una página web guardada ni un PDF.

**Fechas**

- Kit funcionando en todos los ordenadores: **martes 13 de octubre** (el lunes 12 es festivo).
- Primera subida, con la mitad de cada tarea: **lunes 19 de octubre**.
  T1: P1–P6 · T2: E1 y E2 · T3: E4 y E5 · T4: `/salud` y `/analizar` con una línea · T5: interfaz con una respuesta simulada · T6: peticiones con su resultado esperado y primera versión de `explicar_motivo`.
- API e interfaz funcionando juntas: **viernes 23 de octubre**.
- Fecha límite de subida: **lunes 26 de octubre**.
- Ensayo de la defensa, todo el grupo: **jueves 29 de octubre**.
- Entrega final: **viernes 30 de octubre** (a confirmar por el profesor).

## Estructura del repositorio

| Ruta | Contenido |
|---|---|
| `README.md` | Este fichero: reparto, contrato, instalación y ejemplos |
| `requirements.txt` | Librerías necesarias |
| `generar_logs.py`, `logtools.py`, `entrenar.py` | Ficheros del kit |
| `notebooks/P2_analisis_intrusiones.ipynb` | **Cuaderno final** con P1–P13 y la tabla de experimentos (el `analisis.ipynb` del kit, completo) |
| `notebooks/T1_...` a `notebooks/T3_...` | Cuaderno individual de cada tarea |
| `notebooks/plantilla.ipynb` | Plantilla común: el `analisis.ipynb` del kit con cabecera y base común |
| `api/` | API REST (`main.py`, `motivos.py`) y su explicación (`README.md`) |
| `interfaz/` | Interfaz y su explicación (`README.md`) |
| `pruebas/PRUEBAS.md` | Documento de pruebas |
| `pruebas/P2_detector.postman_collection.json` | Colección de Postman con las peticiones de prueba |
| `pruebas/peticiones/` | Cuerpos JSON para probar la API |
| `docs/CONTRATO_API.md` | Detalle de la API para T4, T5 y T6 |
| `docs/diagrama_flujo.md` | Diagrama del flujo del sistema (fase 1) |
| `docs/INFORME.md` | Informe final (máximo 2 páginas) |
| `docs/DEFENSA.md` | Preparación de la defensa oral |
| `docs/REVISION_JEFE.md` | Lista de comprobación del jefe antes de entregar |

## Instalación y ejecución

**Requisitos:** Python 3.10 o superior. Comprobado el 9 de octubre de 2026 con Python 3.13, pandas 3.0 y scikit-learn 1.9.

```bash
# 1. Descargar el repositorio (o en GitHub: Code → Download ZIP)
git clone https://github.com/DannSchwab/ProyectosPython.git
cd ProyectosPython/Proyecto2

# 2. Crear el entorno e instalar las librerías
python -m venv .venv
# Windows (PowerShell):  .venv\Scripts\Activate.ps1
# Windows (cmd):         .venv\Scripts\activate
# Linux / macOS:         source .venv/bin/activate
pip install -r requirements.txt

# 3. Generar el log y las etiquetas con la semilla del grupo
python generar_logs.py --seed ___ --salida auth.log --etiquetas etiquetas.csv

# 4. Entrenar el modelo
python entrenar.py --log auth.log --etiquetas etiquetas.csv --salida modelo.joblib

# 5. Abrir los cuadernos
jupyter notebook
```

Todos los comandos se ejecutan **desde la carpeta `Proyecto2/`**. `modelo.joblib` solo es fiable con la misma versión de scikit-learn con la que se entrenó: si cambias de ordenador, vuelve a ejecutar `entrenar.py`.

### API *(pendiente, T4)*

```bash
uvicorn api.main:app --reload
```

- API: <http://127.0.0.1:8000>
- Documentación interactiva, para probarla desde el navegador: <http://127.0.0.1:8000/docs>

| Método | Ruta | Qué hace |
|---|---|---|
| `GET` | `/salud` | Comprueba que el servicio funciona. Devuelve `{"estado": "ok", ...}` y las características que espera el modelo |
| `POST` | `/analizar` | Recibe líneas de `auth.log`, un umbral y una lista blanca. Devuelve las líneas ignoradas, las IPs analizadas y las sospechosas con su probabilidad y motivo |

### Ejemplos de peticiones

Los cuerpos de las peticiones están en `pruebas/peticiones/`. En Windows, escribe `curl.exe` en lugar de `curl`.

```bash
# Comprobar que la API funciona
curl http://127.0.0.1:8000/salud

# 1. Petición correcta → 200
curl -X POST http://127.0.0.1:8000/analizar -H "Content-Type: application/json" -d @pruebas/peticiones/correcta.json

# 2. Con lista blanca → 200, y 203.0.113.45 no aparece como sospechosa
curl -X POST http://127.0.0.1:8000/analizar -H "Content-Type: application/json" -d @pruebas/peticiones/lista_blanca.json

# 3. Umbral fuera de rango (1.5) → 422
curl -X POST http://127.0.0.1:8000/analizar -H "Content-Type: application/json" -d @pruebas/peticiones/umbral_fuera_rango.json

# 4. Líneas basura → 422
curl -X POST http://127.0.0.1:8000/analizar -H "Content-Type: application/json" -d @pruebas/peticiones/lineas_basura.json
```

Ejemplo de cuerpo (`pruebas/peticiones/lista_blanca.json`, recortado):

```json
{
  "lineas": [
    "Oct  7 09:02:11 srv-web01 sshd[1840]: Failed password for ana from 192.168.1.20 port 40112 ssh2",
    "Oct  7 09:02:19 srv-web01 sshd[1841]: Accepted password for ana from 192.168.1.20 port 40113 ssh2",
    "Oct  7 10:15:30 srv-web01 sshd[2101]: Invalid user admin from 203.0.113.45 port 51234",
    "Oct  7 10:15:30 srv-web01 sshd[2101]: Failed password for invalid user admin from 203.0.113.45 port 51234 ssh2",
    "..."
  ],
  "umbral": 0.7,
  "lista_blanca": ["203.0.113.45"]
}
```

Las mismas peticiones están en la colección de Postman `pruebas/P2_detector.postman_collection.json` (en Postman: **Import** y elegir el fichero). Lo que esperábamos y lo que obtuvimos en cada petición está en [`pruebas/PRUEBAS.md`](pruebas/PRUEBAS.md).

### Interfaz *(pendiente, T5)*

Cómo abrirla y usarla: ver [`interfaz/README.md`](interfaz/README.md).

## Conclusiones

*Pendiente.* Se completa al final con los resultados del cuaderno final (`notebooks/P2_analisis_intrusiones.ipynb`) y del informe (`docs/INFORME.md`).

## Nota sobre la entrega

*Pendiente.* Aquí se anotan las incidencias: tareas no entregadas o completadas por otra persona.
