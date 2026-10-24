def explicar_motivo(fila):
    """Devuelve un motivo en lenguaje humano para una IP sospechosa."""

    motivos = []

    # Comprobamos si se han probado varios usuarios distintos.
    if fila["n_usuarios"] >= 3:
        motivos.append(
            f"prueba {int(fila['n_usuarios'])} usuarios distintos"
        )

    # n_inv cuenta eventos, no intentos independientes.
    if fila["n_inv"] >= 1:
        intentos_aprox = int(fila["n_inv"]) / 2
        motivos.append(
            f"presenta usuarios inexistentes "
            f"(aproximadamente {intentos_aprox:g} intentos)"
        )

    # Comprobamos si hay muchos fallos en cinco minutos.
    if fila["max_fallos_5min"] >= 5:
        motivos.append(
            f"{int(fila['max_fallos_5min'])} fallos en 5 minutos"
        )

    # Comprobamos si hubo un acceso correcto después de varios fallos.
    if fila["n_ok"] >= 1 and fila["n_fallos"] >= 3:
        motivos.append(
            f"consigue entrar después de "
            f"{int(fila['n_fallos'])} fallos"
        )

    # Si no se cumple ninguna regla, usamos el motivo general.
    if not motivos:
        motivos.append(
            "comportamiento parecido a los ataques vistos en el entrenamiento"
        )

    return "; ".join(motivos)
