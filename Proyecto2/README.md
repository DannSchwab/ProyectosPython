# Proyecto P2: Auditar e integrar un detector de intrusiones con IA

Optativa Python para IA, 2º DAM.

La empresa que gestiona el servidor `srv-web01` tiene un detector de intrusiones basado en Machine Learning: lee el log de autenticación SSH y señala las IPs sospechosas. El modelo viene hecho en el kit del profesor. Nuestro trabajo es **entenderlo**, **investigar hasta dónde fiarse de él**, **convertirlo en una API REST con una interfaz** y **decidir con argumentos si se podría usar en producción**.

La API solo informa: nunca bloquea una IP. La decisión final la toma siempre una persona.

## Datos

Log de autenticación SSH **sintético** de `srv-web01`, generado con `generar_logs.py` del kit. Todo el grupo usa la misma semilla: **`--seed 21`**.

Con la semilla 21, `generar_logs.py` debe decir: `12425 lineas en auth.log; 384 IPs (100 atacantes) en etiquetas.csv`. Si te sale otra cosa, revisa el comando: la misma semilla genera siempre exactamente el mismo log. Las IPs públicas son de rangos reservados para documentación (RFC 5737): no pertenecen a nadie real.

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
| Semilla | `--seed 21` para todos. Si ya habías ejecutado algo con otra semilla, hay que repetirlo |
| Ficheros del kit | `logtools.py` y `generar_logs.py` no se modifican |
| Datos y modelo | Se generan dentro de `Proyecto2/`. Nunca se suben `auth.log`, `etiquetas*.csv` ni `modelo.joblib` |
| Cuadernos | Cada uno parte de `notebooks/plantilla.ipynb`. La celda "Base común" no se toca |
| Experimentos | Hipótesis escrita y subida antes de ejecutar. Un solo cambio cada vez |
| Respuestas | Con palabras propias, sin copiar los comentarios del código ni los apuntes |
| Cifras | Solo las obtenidas al ejecutar. Nada inventado |
| Dirección de la API | `http://127.0.0.1:8000`, arrancada con `uvicorn api.main:app` desde `Proyecto2/` |
| `POST /analizar` | Entrada: `lineas`, `umbral` (0 a 1, por defecto 0.7) y `lista_blanca`. Salida: `lineas_ignoradas`, `ips_analizadas` y `sospechosas` (cada una con `ip`, `probabilidad` y `motivo`) |
| Límite | 50 000 líneas por petición |
| Errores | Código 422 con un campo `detail` que lo explica (un texto o una lista de textos). 503 si falta el modelo. Nunca un 500 |
| CORS | La API acepta llamadas desde cualquier página (`CORSMiddleware`), para que la interfaz web funcione se abra como se abra |
| Motivo | T6 programa `explicar_motivo(fila)` en `api/motivos.py`; T4 la llama |
| Interfaz | Página web responsive (HTML + JavaScript con `fetch`) que se ve bien también en el móvil |

El detalle de la API (formatos, errores y fallos conocidos del kit) está en [`docs/CONTRATO_API.md`](docs/CONTRATO_API.md). Si hay que cambiar algo del contrato, se habla antes con el jefe.

## Cómo trabajar

1. Cada persona trabaja solo en sus ficheros (columna **Fichero**), sin tocar los de los demás.
2. Antes de nada, instala el kit y comprueba que funciona (ver [Instalación y ejecución](#instalación-y-ejecución)).
3. T1, T2 y T3: empieza copiando la plantilla (`notebooks/plantilla.ipynb`) con el nombre de tu fichero. Ejecuta las secciones 0 a 5 en orden y después haz tu parte.
4. Comenta el código y explica con tus palabras qué has hecho y por qué. El jefe tiene que entenderlo para poder defenderlo.
5. Experimentos (T2 y T3): escribe las hipótesis y **sube el cuaderno antes de ejecutar**. Después ejecuta y vuelve a subirlo. GitHub guarda la fecha de cada subida, así se ve que la hipótesis iba primero.
6. Termina con un "Hallazgo": 2-3 líneas con datos concretos de tus resultados.
7. Sube tus ficheros a su carpeta con **Add file → Upload files**.
   - Sube **solo tus ficheros**: nunca `auth.log`, `etiquetas.csv`, `modelo.joblib` ni la carpeta `.venv`. Al subir por la web, el `.gitignore` no los frena.
   - Sube el cuaderno **`.ipynb`**, no una página web guardada ni un PDF.

**Fechas**

- Subir lo que haya, aunque esté a medias: **jueves 29 de octubre por la noche**, después del examen. Ese día Argail sube también la API arreglada, porque la interfaz y las pruebas dependen de ella.
- Fecha límite de subida: **viernes 30 de octubre a las 21:00**.
- Entrega final: **sábado 31 de octubre a las 23:59**.
- Defensa oral y ensayo: fecha por confirmar.

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
python generar_logs.py --seed 21 --salida auth.log --etiquetas etiquetas.csv

# 4. Entrenar el modelo
python entrenar.py --log auth.log --etiquetas etiquetas.csv --salida modelo.joblib

# 5. Abrir los cuadernos
jupyter notebook
```

Todos los comandos se ejecutan **desde la carpeta `Proyecto2/`**. `modelo.joblib` solo es fiable con la misma versión de scikit-learn con la que se entrenó: si cambias de ordenador, vuelve a ejecutar `entrenar.py`.

### API

```bash
uvicorn api.main:app --reload
```

- API: <http://127.0.0.1:8000>
- Documentación interactiva, para probarla desde el navegador: <http://127.0.0.1:8000/docs>

| Método | Ruta | Qué hace |
|---|---|---|
| `GET` | `/salud` | Comprueba que el servicio funciona. Devuelve `{"estado": "ok", ...}` y las características que espera el modelo |
| `POST` | `/analizar` | Recibe líneas de `auth.log`, un umbral y una lista blanca. Devuelve las líneas ignoradas, las IPs analizadas y las sospechosas con su probabilidad y motivo |

El umbral por defecto es 0.7 porque lo fija el enunciado, pero se puede enviar otro en cada petición; en el informe recomendamos 0.5. Cómo funciona la API por dentro (validaciones, errores y lista blanca): [`api/README.md`](api/README.md).

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

### Interfaz

1. Con la API en marcha, abre `interfaz/index.html` en el navegador (doble clic). No necesita servidor propio.
2. Carga `auth.log` en «Cargar un fichero de log» o pega las líneas, ajusta el umbral y, si hace falta, escribe la lista blanca (IPs separadas por comas).
3. Pulsa **Analizar log**. Sale una tabla con las IPs sospechosas, ordenadas de mayor a menor probabilidad, con su motivo. Los errores de la API aparecen en un recuadro rojo con un mensaje comprensible. En el móvil, cada IP se ve como una tarjeta.

Validaciones y problemas frecuentes: [`interfaz/README.md`](interfaz/README.md).

## Conclusiones

Resultados del cuaderno final ([`notebooks/P2_analisis_intrusiones.ipynb`](notebooks/P2_analisis_intrusiones.ipynb)), con la semilla 21. El detalle está en el [informe](docs/INFORME.md) y en la [preparación de la defensa](docs/DEFENSA.md).

- **El sistema funciona de principio a fin.** La API valida la entrada, respeta la lista blanca, explica cada IP con un motivo y nunca bloquea; la interfaz la consume desde el ordenador y desde el móvil; las 5 pruebas de `PRUEBAS.md` dan el código esperado.
- **Con nuestros datos el modelo acierta casi todo, pero un solo número engaña.** Con el reparto de referencia no falla ninguna de las 96 IPs de prueba; con 10 repartos distintos, el F1 va de 0,958 a 1,000 (media 0,984). Los fallos son casi siempre las mismas IPs difíciles: un script de monitorización legítimo con 37 fallos y un atacante con solo 4 intentos en 27 minutos.
- **Es mucho mejor que una regla simple** (F1 de 0,26 a 0,36), pero los datos son sintéticos y muy fáciles: quitar cualquier característica no cambia nada, y el log «nuevo» de E5 (F1 0,990) sale del mismo generador.
- **El umbral importa con datos nuevos.** Con el 0,7 de la API se escapan 7 de 100 atacantes (5 de ellos, equipos internos: el modelo ha aprendido que lo interno suele ser legítimo); con 0,5, solo 2, y en ninguno de los dos casos se marca una IP legítima. Recomendamos enviar 0,5 en cada petición.
- **Recomendación:** usarlo solo como ayuda para una persona, nunca para bloquear automáticamente, y antes de producción probarlo con logs reales y añadir autenticación, HTTPS y límites de peticiones.

## Nota sobre la entrega

- **T3 (Noel):** en la fecha límite (viernes 30, 21:00) el cuaderno tenía las hipótesis de E4–E7 y el código preparado, pero no estaba ejecutado ni tenía resultados. Daniel lo ejecutó y lo completó el sábado 31 (resultados y explicaciones, comprobación de las IPs mal clasificadas, tabla de registro, P13 y sección 8) sin cambiar las hipótesis de Noel. Queda indicado al principio del cuaderno.
- **T7 (Daniel):** cuaderno final, informe y defensa, a partir de los borradores de cada uno. En el cuaderno final añadió dos comprobaciones, marcadas como tales: qué IPs fallan en cada reparto (E4 y E6) y qué pasa con el umbral de la API con los datos nuevos de E5. Esta última se hizo sin hipótesis previa, al revisar el umbral.
- **Retoques del jefe en ficheros de otros:** en `pruebas/PRUEBAS.md` (Jorge), el 30/10 Daniel ajustó el resultado esperado de la prueba 5 al contrato, rehízo el esquema de la sección 5 con las piezas reales y añadió a la pregunta 1 los datos de E1 y el riesgo de la lista blanca. En `api/README.md` (Argail) se puso la semilla del grupo (21) en el comando de ejemplo.
