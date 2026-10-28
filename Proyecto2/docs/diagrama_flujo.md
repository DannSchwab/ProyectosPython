# Diagrama del flujo del sistema

**T1 Comprender** · Autora: Jia Xi

El sistema transforma las líneas de `auth.log` en eventos, agrupa los eventos por IP y utiliza 11 características numéricas. El entrenamiento y la detección de nuevas IP son pasos separados.

```mermaid
flowchart TD
    A["auth.log<br/>Ejemplo procesado: 2026-10-07 00:00:00<br/>acceso_ok · usuario backup · IP 10.0.0.5"]
    B["cargar_log()<br/>Texto del log → DataFrame df<br/>Cada fila representa un evento"]
    C["construir_features(df)<br/>Eventos agrupados por IP → matriz X<br/>11 características numéricas"]
    A -->|"Líneas de texto del registro"| B
    B -->|"Eventos: timestamp, tipo, usuario, IP, puerto y usuario_invalido"| C

    subgraph ENTRENAMIENTO["Entrenamiento y evaluación"]
      D["Etiquetas y<br/>y: 0 = legítima, 1 = atacante"]
      E["Separar X e y<br/>en entrenamiento y prueba"]
      F["RandomForestClassifier<br/>Entrenar con X_train e y_train"]
      G["Evaluar con X_test<br/>que el modelo no ha visto"]
      E -->|"X_train, X_test, y_train, y_test"| F
      D -->|"Etiquetas reales"| E
      F -->|"Modelo entrenado"| G
    end
    C -->|"X: 384 IP × 11 características (en estos datos)"| E

    subgraph DETECCION["Detección de nuevas IP"]
      H["Nueva tabla de características<br/>11 valores por IP"]
      I["modelo.predict_proba(X_nuevo)<br/>Probabilidad para cada clase"]
      J{"¿Probabilidad de atacante ≥ 0,7?"}
      K["Marcar IP como sospechosa"]
      L["No marcar como sospechosa"]
      M["Revisión humana<br/>No se bloquea automáticamente"]
      H -->|"X_nuevo: matriz numérica"| I
      I -->|"Probabilidad de la clase atacante"| J
      J -->|"Sí"| K
      J -->|"No"| L
      K --> M
      L --> M
    end
    F -->|"Modelo ya entrenado"| I
```

## Explicación de cada paso

1. **`auth.log` → eventos:** `cargar_log()` lee las líneas de texto y las convierte en un DataFrame llamado `df`. Cada fila representa un evento de autenticación.
2. **Eventos → características por IP:** `construir_features()` agrupa los eventos por IP y calcula 11 características, como `n_eventos`, `n_fallos`, `n_ok`, `n_usuarios` y `max_fallos_5min`. El resultado es la matriz `X`.
3. **Entrenamiento y evaluación:** el modelo `RandomForestClassifier` aprende con `X_train` e `y_train`. Después se evalúa con `X_test` e `y_test`, que se reservaron y no se utilizaron para entrenarlo.
4. **Detección:** para analizar nuevas IP, el modelo usa `predict_proba()` para obtener una probabilidad. Se compara la probabilidad de la clase atacante con el umbral `0,7`: si lo alcanza, la IP se marca como sospechosa.
5. **Decisión final:** el sistema informa de las IP sospechosas, pero no las bloquea automáticamente. Una persona debe revisar el resultado.

El ejemplo de `10.0.0.5` procede de una fila del DataFrame que aparece en el cuaderno. Las 11 características y el umbral `0,7` se han tomado de la información disponible en el proyecto.
