# Informe: detector de intrusiones SSH con IA

P2 · Python para IA, 2º DAM · Daniel (jefe), Jia Xi, Sergio, Noel, Argail, Alejandro y Jorge · Semilla 21 · Cifras de `notebooks/P2_analisis_intrusiones.ipynb`

## 1. Qué hace el sistema

El detector lee el registro de autenticación SSH (`auth.log`) del servidor `srv-web01` y señala las IP que parecen atacarlo. Convierte cada línea en un evento (fecha, tipo, usuario, IP y puerto), los agrupa por IP, porque lo que delata a un atacante es su comportamiento y no una línea suelta, y calcula 11 características por IP, como los fallos, los usuarios distintos probados o los fallos en 5 minutos. Un bosque aleatorio (200 árboles de decisión que votan), entrenado con ejemplos etiquetados, da la probabilidad de que cada IP sea atacante. Si llega al umbral (0,7 por defecto, ajustable en cada petición), la IP sale como sospechosa con su probabilidad y un motivo legible, como «prueba 8 usuarios distintos». Nunca bloquea: avisa, y decide una persona.

## 2. Qué hemos descubierto

Hicimos los 7 experimentos del kit y uno propio (E8), con la hipótesis escrita antes de ejecutar.

- **Con el reparto de referencia acierta todo, pero en parte es suerte.** En las 96 IP de prueba no falla ninguna (F1 1,000). Con 10 repartos distintos (E4), el F1 va de 0,958 a 1,000 (media 0,984) y solo 4 son perfectos. Los fallos son casi siempre las mismas dos IP difíciles: un script de monitorización legítimo con 37 fallos (`192.168.1.249`) y un atacante con solo 4 intentos en 27 minutos (`198.51.100.26`).
- **Mucho mejor que una regla simple, pero con datos muy fáciles.** La regla «N fallos en 5 minutos» se queda en un F1 de 0,26 a 0,36 (E3); quitar cualquier característica no cambia nada (E2) y un solo árbol de decisión también acierta todo (E8).
- **El umbral apenas se nota con nuestros datos, pero sí con datos nuevos.** Con nuestro reparto, entre 0,1 y 0,95 solo cambian 1 o 2 IP, como el ruido de E4 (E1). Con el log de otra semilla (E5), con umbral 0,5 se escapan 2 de 100 atacantes (F1 0,990) y con el 0,7 que trae la API, 7, de los que 5 son equipos internos comprometidos. Con solo 3 atacantes en la prueba (E6) el recall salta entre 1,00 y 0,67, y sin etiquetas (E7) el mejor F1 es 0,847.

## 3. Hasta dónde fiarse

- **Falsos positivos.** El script `192.168.1.249` parece un ataque: bloquearlo cortaría un servicio de la empresa, y al director le podría pasar lo mismo si se equivoca de contraseña varias veces. Por eso la API solo informa, una persona revisa cada aviso y hay una lista blanca corta y revisada (si un equipo de la lista se ve comprometido, sus ataques no se verían).
- **Azar y pocos datos.** Con 25 atacantes de prueba, cada uno mueve el recall 4 puntos; con 3 (E6), 33. Una diferencia de 1 IP entre dos pruebas es ruido.
- **Datos sintéticos.** Todo sale de `generar_logs.py`; el log «nuevo» de E5 es el mismo generador con otra semilla (hasta repite el script de monitorización). No demuestra que funcione con logs reales.
- **Sesgos.** Casi todas las IP legítimas son internas (253 de 284) y casi todos los atacantes, externos (89 de 100). El modelo lo ha aprendido: con datos nuevos y umbral 0,7, 5 de los 7 atacantes que se escapan son internos. Y quien se conecta desde fuera (teletrabajo) parte con más sospecha.
- **Fuga de datos.** `n_ok` cuenta accesos correctos, que en un atacante solo existen cuando ya ha entrado: un modelo que dependiera de ella avisaría tarde (aquí quitarla no cambia nada, E2). Evaluar con IP del entrenamiento también infla el resultado: el 100 % que da la API con el `auth.log` completo en la demo no vale como medida, porque el modelo ya vio el 75 % de esas IP.
- **Cambios de táctica.** Se le escapan los ataques lentos contra un solo usuario, y uno repartido entre 500 IP apenas dejaría rastro por IP: harían falta señales globales (fallos por usuario atacado o por minuto en el servidor) y reentrenar cuando cambien los ataques.
- **Privacidad.** Las IP, los nombres de usuario (a veces, una contraseña tecleada en ese campo) y las horas de conexión son datos personales: hay que guardar solo lo necesario y el tiempo justo, limitar el acceso y justificar el tratamiento (interés legítimo en proteger el servidor). Que decida una persona va en la línea del artículo 22 del RGPD.

## 4. Recomendación

Sí, como **herramienta de apoyo** que avisa y nunca bloquea, y después de probarlo con logs reales del servidor, porque solo lo hemos evaluado con datos inventados.

- **Umbral 0,5**, enviado en cada petición (la API trae 0,7 por defecto porque lo pide el enunciado). Con datos nuevos, 0,5 deja escapar 2 de 100 atacantes y 0,7, 7, sin marcar ninguna IP legítima. Con datos muy sensibles, 0,3: no se escapa ninguno, a cambio de avisos falsos como el del script de monitorización. El valor exacto se ajustaría con logs reales.
- **Revisión humana:** un administrador revisa cada aviso (motivo y líneas del log) antes de actuar, y la lista blanca se revisa periódicamente.
- **Monitorización:** IP marcadas al día, avisos que resultan falsos y cambios en los datos (ataques nuevos, más conexiones externas). Si empeora, se reentrena y se cambia el modelo sin parar el servicio: la versión nueva se carga y se comprueba antes de sustituir a la anterior.
- **Antes de ponerla en Internet:** clave de API, HTTPS, límite de peticiones por minuto y CORS limitado a la interfaz autorizada.

## 5. Esquema de la integración

```text
Interfaz web (interfaz/index.html) u otro cliente: panel, app móvil, tickets
  │  POST /analizar · JSON {lineas, umbral, lista_blanca}
  ▼
API REST (FastAPI, api/main.py): valida la entrada (422 si no vale, 503 sin modelo)
  ▼
logtools.py (importado, no copiado): eventos → 11 características por IP
  │  una fila por IP (sin las de la lista blanca)
  ▼
modelo.joblib (cargado una sola vez al arrancar): probabilidad ≥ umbral → sospechosa
  ▼
api/motivos.py: explicar_motivo() → «prueba 8 usuarios distintos; …»
  │  JSON {lineas_ignoradas, ips_analizadas, sospechosas: [ip, probabilidad, motivo]}
  ▼
Interfaz: tabla ordenada por probabilidad o error comprensible → decide una persona
```
