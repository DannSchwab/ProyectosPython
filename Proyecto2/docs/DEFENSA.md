# Preparación de la defensa oral

**10 minutos:** 3 minutos de demostración (API e interfaz funcionando) y preguntas del profesor. **Todos tenemos que poder responder cualquier pregunta**: cada uno preparó una, pero el profesor puede preguntar a quien quiera. Las cifras salen de `notebooks/P2_analisis_intrusiones.ipynb` (semilla 21) y de la API funcionando.

## Antes de entrar (preparado en el ordenador de la demo)

1. Desde `Proyecto2/`, con el entorno activado: generar los datos con `--seed 21` y entrenar el modelo (ver el README).
2. Arrancar la API: `uvicorn api.main:app` y dejar la terminal a la vista.
3. Abrir en el navegador `interfaz/index.html` y, en otra pestaña, `http://127.0.0.1:8000/salud`.
4. Tener a mano `auth.log` y la colección de Postman o `http://127.0.0.1:8000/docs`.
5. Plan B si algo falla: las capturas de `pruebas/capturas/` y las salidas del cuaderno final.

## Guion de la demo (3 minutos, la hace Daniel)

| Tiempo | Qué se hace | Qué se dice |
|---|---|---|
| 0:00–0:20 | Terminal con `uvicorn` en marcha y pestaña de `/salud` | «La API carga el modelo una sola vez al arrancar. `/salud` dice que está cargado y qué 11 características espera». |
| 0:20–1:10 | Interfaz: en «Cargar un fichero de log», elegir `auth.log`; umbral 0,7; **Analizar log** | Salen 384 IP analizadas y 100 sospechosas, ordenadas por probabilidad, con su motivo (por ejemplo, «prueba 12 usuarios distintos; … 194 fallos en 5 minutos»). «Aquí acierta los 100 atacantes, pero no vale como medida: el modelo ya vio el 75 % de estas IP al entrenar. La medida honesta está en el cuaderno (E4)». |
| 1:10–1:50 | Umbral 0,3 y volver a analizar; bajar al final de la tabla | Salen 101: la nueva es `192.168.1.249` (32.0 %, «37 fallos de contraseña contra el mismo usuario»), el script de monitorización legítimo. «Es un falso positivo. Por eso la API no bloquea nada: avisa y decide una persona». |
| 1:50–2:10 | Escribir `192.168.1.249` en la lista blanca y analizar | Vuelven a salir 100 y 383 IP analizadas: la lista blanca la excluye. |
| 2:10–2:40 | Errores: lista blanca `hola`; después, pegar dos líneas basura; después, umbral 1,5 | 422 con mensaje claro: «'hola' no es una dirección IP válida…» y «No se ha reconocido ninguna línea válida de auth.log…». Con 1,5 avisa la propia página; enviado directamente a la API (prueba 3 de Postman), la respuesta es un 422. |
| 2:40–3:00 | F12 → vista de móvil | La tabla se convierte en tarjetas, sin desplazamiento lateral. Cierre: «Solo informa; la decisión final es siempre de una persona». |

Comprobado el 31/10 con la semilla 21: con el `auth.log` completo salen 100 sospechosas con umbral 0,7, 101 con 0,3 (la nueva es `192.168.1.249`) y 99 con 0,8 (deja fuera a `203.0.113.86`, con un 72 %).

## Preguntas

| # | Pregunta (del enunciado) | La preparó | Borrador original |
|---|---|---|---|
| 1 | Si el detector bloquea por error la dirección del director, ¿qué ha fallado y cómo lo evitarías? | Jorge | `pruebas/PRUEBAS.md` |
| 2 | ¿Qué te enseña el experimento E4 sobre fiarse de un solo resultado? | Noel (completado por Daniel) | `notebooks/T3_azar_y_datos_nuevos.ipynb` |
| 3 | ¿Por qué el modelo funciona tan bien con estos datos? ¿Qué esperarías con logs reales? | Noel (completado por Daniel) | `notebooks/T3_azar_y_datos_nuevos.ipynb` |
| 4 | ¿Qué característica parece que "hace trampa" o depende de cómo se generó el dataset, y por qué? | Sergio | `notebooks/T2_umbral_y_caracteristicas.ipynb` |
| 5 | ¿Qué pasa si el atacante usa 500 IPs a la vez con pocos intentos cada una? | Jia Xi | `notebooks/T1_comprender.ipynb` |
| 6 | ¿Cómo actualizarías el modelo en producción sin parar el servicio? | Argail | `api/README.md` |
| 7 | ¿Qué datos personales hay en los logs y qué obligaciones implica tratarlos? | Alejandro | `interfaz/README.md` |
| 8 | ¿Qué añadirías a la API antes de ponerla en Internet (autenticación, límites, HTTPS)? | Argail | `api/README.md` |

### 1. Bloqueo del director por error

Es un **falso positivo**: el modelo ha marcado como atacante una IP legítima. Pasa en nuestros datos: con umbral 0,1, E1 marca 1 IP legítima, y el script de monitorización `192.168.1.249` (37 fallos de contraseña) sale como sospechoso cada vez que cae en la prueba (E4) y en la demo con umbral 0,3. Al director le podría pasar si se equivoca varias veces de contraseña o se conecta desde una red nueva. Cómo evitarlo: que la herramienta **no bloquee** (nuestra API solo informa), que una persona revise el aviso con su motivo, un umbral adecuado y la **lista blanca** para las IP de confianza. La lista blanca tiene un riesgo: si el equipo del director se viera comprometido, sus ataques no se señalarían, así que debe ser corta y revisada.

### 2. Qué enseña E4

Que un solo resultado puede ser optimista por suerte. Con el reparto 42 el F1 es 1,000, pero con 10 repartos va de 0,958 a 1,000 (media 0,984) y solo 4 son perfectos. No es que el modelo sea peor en unos repartos: depende de qué IP difíciles caen en la prueba. `192.168.1.249` y `198.51.100.26` fallan siempre que caen en ella, y en el reparto 42 no cae ninguna de las dos. Hay que repetir con varios repartos y dar la media y el rango. Además, una diferencia de 1 IP entre dos pruebas (como entre umbrales en E1) es del tamaño del ruido, no una mejora real.

### 3. Por qué funciona tan bien y qué esperar con logs reales

Porque los datos los genera `generar_logs.py` con patrones muy marcados: la mediana de fallos es 24 en los atacantes y 1 en las legítimas, y la de usuarios probados, 8,5 frente a 1; casi todos los atacantes son externos (89 de 100) y casi todas las legítimas, internas (253 de 284). Además, muchas características dicen lo mismo: quitando cualquiera, el F1 sigue en 1,000 (E2). Con otra semilla (E5) el F1 es 0,990, pero es el mismo generador. Con logs reales esperaríamos peores resultados: ataques lentos o repartidos, usuarios legítimos desde fuera, scripts mal configurados y ataques nuevos. Ya se ve un aviso: con datos nuevos y umbral 0,7 se escapan 7 de 100 atacantes, 5 de ellos internos. Antes de usarlo habría que evaluarlo con logs reales etiquetados.

### 4. La característica que "hace trampa"

`es_interna` y `n_ok`. Casi todas las IP legítimas son internas (253 de 284) y casi todos los atacantes, externos (89 de 100), y eso lo decide el programa que generó el log, no la realidad. El modelo lo ha aprendido: con datos nuevos y umbral 0,7, 5 de los 7 atacantes que se escapan son equipos internos comprometidos. `n_ok` cuenta accesos correctos, que en un atacante solo existen cuando ya ha entrado; en nuestros datos ningún atacante tiene 2 o más. Aun así, quitando las dos a la vez el modelo no empeora (F1 1,000), porque otras características dicen lo mismo.

### 5. 500 IP con pocos intentos cada una

El modelo mira cada IP por separado, así que con pocos fallos por IP cada una parecería un usuario que se equivoca, y lo más probable es que no las detectara. Ya ocurre a pequeña escala: los atacantes que se escapan en E4 y E6 son los lentos, con intentos espaciados contra un solo usuario (`198.51.100.26`: 4 fallos en 27 minutos). Además, el modelo no ha visto nunca este tipo de ataque al entrenar. Para detectarlo habría que añadir señales globales, como los fallos por usuario atacado o los fallos de todo el servidor por minuto, y que una persona revise los picos.

### 6. Actualizar el modelo sin parar el servicio

Se entrena la versión nueva en un fichero aparte y se comprueba que carga y pasa las pruebas. Después, la API carga esa versión en memoria y cambia la referencia al modelo activo de golpe: las peticiones en curso terminan con el anterior. Si algo falla, se mantiene la versión anterior. Otra opción es arrancar una instancia nueva de la API con el modelo nuevo y pasarle el tráfico cuando esté lista. Nuestra API carga el modelo una sola vez al arrancar, así que la recarga en caliente habría que programarla. Conviene que la respuesta incluya la versión del modelo.

### 7. Datos personales en los logs

Las IP de origen (son datos personales porque pueden identificar a una persona), los nombres de usuario, que incluyen nombres de empleados y, a veces, una contraseña escrita por error en el campo de usuario, y las horas de conexión. Obligaciones: no guardarlos más tiempo del necesario, tener una base legal (el interés legítimo en proteger el servidor), usar solo los datos necesarios, limitar el acceso al personal autorizado, protegerlos frente a manipulaciones e informar a los usuarios. Como la API no bloquea y decide una persona, va en la línea del artículo 22 del RGPD (no ser objeto de decisiones tomadas solo por una máquina).

### 8. Antes de poner la API en Internet

Autenticación (por ejemplo, una clave de API) para que solo llamen las aplicaciones autorizadas; HTTPS para cifrar las comunicaciones; límite de peticiones por minuto, además del límite actual de 50 000 líneas por petición; CORS limitado a la dirección de la interfaz, porque ahora acepta cualquier origen (y CORS no sustituye a la autenticación); errores sin información interna; registro de la actividad sin guardar datos sensibles innecesarios; y desplegarla de forma controlada después de probarla.

## Otras preguntas probables

- **¿Por qué la API usa 0,7 si recomendáis 0,5?** Porque el enunciado fija 0,7 por defecto, pero el umbral se envía en cada petición. Con datos nuevos, 0,7 deja escapar 7 atacantes de 100 y 0,5, 2, sin marcar ninguna IP legítima en ninguno de los dos casos.
- **¿Por qué se agrupa por IP?** Porque una línea suelta no dice nada y el comportamiento de una IP durante el día sí: muchos fallos, muchos usuarios o ráfagas.
- **¿Qué error es más grave, un falso positivo o un falso negativo?** Para la seguridad, el falso negativo (un atacante que se cuela). Por eso preferimos un umbral algo bajo, con revisión humana que descarte los avisos falsos.
- **¿Qué hacen `stratify` y `class_weight="balanced"`?** `stratify` mantiene la proporción de atacantes (26 %) en entrenamiento y prueba; `class_weight` da más peso a la clase minoritaria para que el modelo no aprenda a decir siempre «legítima».
- **¿Qué pasa con una línea casi válida (mes inexistente, hora 25)?** La API la cuenta en `lineas_ignoradas` y analiza el resto: nunca devuelve un 500 (prueba 5 de `PRUEBAS.md`).
- **¿Por qué hace falta CORS?** Porque la interfaz se abre desde otro origen (un fichero o una página distinta) y, sin esa cabecera, el navegador bloquea la respuesta de la API aunque esta funcione.

## Cifras clave

| Dato | Valor |
|---|---|
| Datos (semilla 21) | 12 425 líneas, 384 IP, 100 atacantes (26 %); prueba: 96 IP (71 legítimas y 25 atacantes) |
| Referencia (reparto 42) | Matriz `[[71, 0], [0, 25]]`: precisión, recall y F1 = 1,000 |
| E1 umbral | 0,1: 1 legítima marcada · 0,3 y 0,5: sin errores · 0,8: 1 atacante colado · 0,95: 2 colados |
| E2 quitar características | Quitando cualquiera, F1 = 1,000 |
| E3 regla `max_fallos_5min ≥ N` | F1 0,360 (N = 3), 0,263 (N = 5) y 0,333 (N = 10), frente a 1,000 del modelo |
| E4 azar del reparto | F1 de 0,958 a 1,000, media 0,984; 4 de 10 perfectos |
| E5 datos nuevos (semilla 999) | F1 0,990: 0 legítimas marcadas y 2 de 100 atacantes colados |
| Umbral con datos nuevos | 0,3: 1 legítima marcada y 0 colados · 0,5: 0 y 2 · 0,7: 0 y 7 (5 internos) |
| E6 pocos atacantes | 12 de 296 IP (4 %), 3 en la prueba; recall 1,00 en 8 repartos y 0,67 en 2 |
| E7 sin etiquetas | F1 0,333 (0,05), 0,547 (0,1), 0,847 (0,25) y 0,797 (0,4) |
| E8 árbol de decisión | F1 1,000 |
| `es_interna` | 253 de 284 legítimas son internas; 89 de 100 atacantes son externos |
| API con el `auth.log` completo | 0,7: 100 sospechosas · 0,3: 101 (+ `192.168.1.249`) · 0,8: 99 |
