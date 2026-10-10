# Revisión del jefe

Lista de comprobación para revisar cada subida, entender lo que ha hecho cada uno y corregir errores antes de entregar.

En GitHub, el botón **History** de cada fichero muestra todas sus subidas con fecha y autor.

## En cada subida

- [ ] Está en su carpeta y con el nombre del reparto.
- [ ] Es el tipo de fichero correcto: el `.ipynb` se abre como cuaderno en Jupyter o VS Code (no es una página web guardada ni un PDF).
- [ ] No se ha subido `auth.log`, `etiquetas*.csv`, `modelo.joblib` ni `.venv`.
- [ ] No se han tocado ficheros de otros, ni `logtools.py` o `generar_logs.py`.

## Por tarea

| Tarea | Comprobar | Tienes que poder explicar |
|---|---|---|
| **T1** Jia Xi | P1–P11 con palabras propias (compáralas con los comentarios de `logtools.py`) y con ejemplos concretos del log. El diagrama se ve como imagen en GitHub y cada flecha dice qué datos viajan | Cómo pasa una línea de texto a una fila de números por IP, y por qué se agrupa por IP |
| **T2** Alejandro | En **History**, la primera subida tiene las hipótesis y todavía no los resultados. Un solo cambio por experimento. Tabla con precisión, recall, F1 y errores. E8 hecho | Qué pasa al subir y bajar el umbral, y qué característica es sospechosa |
| **T3** Noel | Lo mismo que T2 sobre las hipótesis. Ha generado `auth_b.log` y `auth_poco.log` con los comandos del cuaderno | Qué es ruido y qué es una diferencia real (E4), y por qué funciona tan bien con datos sintéticos |
| **T4** Jorge | Arranca con `uvicorn api.main:app` desde `Proyecto2/`. El modelo se carga fuera de las funciones de las rutas (una sola vez). Importa `logtools`, no copia su código. Con las peticiones de `pruebas/peticiones/` nunca da un 500. La IP de la lista blanca nunca sale. Con más de 50 000 líneas da 422 | Qué ocurre, paso a paso, desde que llega una petición hasta que sale la respuesta |
| **T5** Sergio | Llama a la API, no abre `modelo.joblib`. Funciona tanto cargando un fichero como pegando líneas. Muestra los errores de forma comprensible, tanto si `detail` es un texto como si es una lista | Cómo viaja la petición de la interfaz a la API y de vuelta |
| **T6** Argail | Cada petición tiene "Esperado" escrito antes que "Obtenido", con salida o captura. `explicar_motivo` devuelve un texto en todos los casos, también cuando no se cumple ninguna regla, y tiene en cuenta que `n_inv` cuenta dos líneas por intento | Por qué se marca una IP, en palabras que entendería un administrador |

## Revisión final (26 a 29 de octubre)

- [ ] Copiar las respuestas y la tabla de T1, T2 y T3 a `notebooks/P2_analisis_intrusiones.ipynb`.
- [ ] Ejecutar el cuaderno final desde cero (en Jupyter: *Kernel → Restart Kernel and Run All Cells*) con la semilla del grupo, y comprobar que los números del informe coinciden con los del cuaderno.
- [ ] Probar API e interfaz juntas en un ordenador distinto al de quien las programó, siguiendo solo el README.
- [ ] Informe de 2 páginas como máximo.
- [ ] README: rellenar la semilla y el tipo de interfaz, quitar los "pendiente", escribir las Conclusiones y la Nota sobre la entrega.
- [ ] Ensayo de la demo de 3 minutos y de las 8 preguntas (jueves 29).
