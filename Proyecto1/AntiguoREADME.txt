# Proyecto P1: Análisis exploratorio del Titanic (numpy y pandas)

Optativa Python para IA, 2º DAM.

## Dataset

Titanic (versión de seaborn), en `Data/titanic.csv`. Es el dataset recomendado en el enunciado: público, 891 filas y columnas numéricas y categóricas.

## Reparto

| Persona | Nombre | Tarea | Qué entrega | Fichero |
|---|---|---|---|---|
| P1 | JiaXi | T1 Carga e inspección | head, info, describe, shape y diccionario de datos | T1_carga_inspeccion.ipynb |
| P2 | Alejandro | T2a Nulos | isna().sum(), decisión y justificación por columna | T2a_nulos.ipynb |
| P3 | Noel | T2b Duplicados | duplicated(), decisión justificada y chequeo de valores raros | T2b_duplicados.ipynb |
| P4 | Jorge | T3a Franja de edad | columna franja_edad con numpy, sin bucles | T3a_franja_edad.ipynb |
| P5 | Sergio | T3b Normalización | columnas tarifa_norm y tam_familia con numpy, sin bucles | T3b_normalizacion.ipynb |
| P6 | Argail | T4a Filtrado | 2 filtros con condiciones distintas y 2 estadísticas sobre ellos | T4a_filtrado.ipynb |
| P7 | Daniel(Ainoha dejó el grado) | T4b Groupby | 4 agregaciones por categoría (sexo, clase, sexo y clase) | T4b_groupby.ipynb |
| Jefe | Daniel | T5 y revisión final | conclusiones, unión de notebooks y entrega | P1_analisis_titanic.ipynb |

## Contrato (todos seguimos esto)

| Decisión | Valor |
|---|---|
| Nombres de columnas | Los del CSV, sin renombrar (age, sex, pclass, survived...) |
| Nulos | age: mediana. embarked y embark_town: moda. deck: se elimina la columna |
| Duplicados | Nadie elimina filas hasta que P3 decida |
| Columnas nuevas | franja_edad, tarifa_norm, tam_familia (tam_familia = sibsp + parch + 1) |
| Franjas de edad | 0-12, 13-17, 18-59, 60+ |
| Bucles for sobre filas | Prohibidos, todo vectorizado |

## Cómo trabajar

1. Cada persona trabaja solo en su notebook, sin tocar los de los demás.
2. Empieza copiando la plantilla (`notebooks/plantilla.ipynb`).
3. Comenta el código y organízalo por tareas.
4. Termina con una celda de texto llamada "Hallazgo": 2-3 líneas con datos concretos.
5. Sube tu notebook a la carpeta `notebooks/` con Add file → Upload files.

Fecha límite de subida: 29 de septiembre. Entrega final: 30 de septiembre.

## Estructura del repositorio

| Ruta | Contenido |
|---|---|
| `Data/titanic.csv` | Dataset de trabajo |
| `notebooks/P1_analisis_titanic.ipynb` | **Notebook final** con todo el análisis (T1-T5) |
| `notebooks/T1_...` a `notebooks/T5_...` | Notebook individual de cada tarea |
| `notebooks/plantilla.ipynb` | Plantilla común usada por el equipo |

## Conclusiones

El análisis completo está en `notebooks/P1_analisis_titanic.ipynb`.

1. **El sexo es la variable que más determina la supervivencia**: sobrevivió el 74,20% de las mujeres frente al 18,89% de los hombres.
2. **La clase del billete también influye, de forma escalonada**: 62,96% de supervivencia en 1ª clase, 47,28% en 2ª y 24,24% en 3ª.
3. **Sexo y clase se combinan, no actúan por separado**: casi todas las mujeres de 1ª y 2ª clase sobrevivieron (96,81% y 92,11%), pero solo la mitad de las de 3ª (50,00%); entre los hombres la supervivencia fue baja en todas las clases.
4. **La edad influye, sobre todo en los extremos**: la correlación entre edad y supervivencia es casi nula (-0,065), pero los niños de 0-12 años tuvieron la mayor tasa de supervivencia (57,97%) y los mayores de 60 la menor (26,92%).
5. **Los datos tienen limitaciones**: cerca del 20% de las edades son estimaciones (mediana imputada) y faltan columnas identificadoras (nombre, billete), por lo que no se puede confirmar si las 107 filas repetidas son pasajeros distintos; se decidió no eliminarlas (ver T2b).

## Nota sobre la entrega

- **T2b (duplicados):** Noel subió la detección de duplicados, pero el fichero era una página web guardada desde Colab y no un notebook. Daniel pasó su código a un notebook y completó el análisis, la decisión y la revisión de valores.
- **T4b (groupby):** no se entregó; la completó Daniel como jefe de grupo ante la ausencia de Ainoha.
