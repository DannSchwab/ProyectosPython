// Dirección de la API (definida en el contrato del proyecto)
const API_URL = 'http://127.0.0.1:8000/analizar';

// Límite de líneas por petición (contrato del proyecto y max_length de la API)
const LIMITE_LINEAS = 50000;

const form = document.getElementById('form-analisis');
const divErrores = document.getElementById('errores');
const divResultados = document.getElementById('resultados');
const botonAnalizar = document.getElementById('boton-analizar');
const inputFichero = document.getElementById('fichero');
const textareaLog = document.getElementById('log');

// Escapa el texto antes de meterlo en innerHTML.
// El log y la respuesta de la API pueden contener caracteres como < o >,
// y sin escapar se podría ejecutar código inyectado en la página.
function esc(texto) {
    return String(texto).replace(/[&<>"']/g, c => ({
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#39;'
    }[c]));
}

function mostrarError(htmlMensaje) {
    divErrores.innerHTML = htmlMensaje;
    divErrores.hidden = false;
}

function limpiarPantalla() {
    divErrores.innerHTML = '';
    divErrores.hidden = true;
    divResultados.innerHTML = '';
    divResultados.hidden = true;
}

// Si la API devuelve un número lo usamos tal cual; si devuelve una lista, contamos sus elementos
function comoNumero(valor) {
    return Array.isArray(valor) ? valor.length : valor;
}

// Formatea la probabilidad (0 a 1) como porcentaje
function formatearProbabilidad(p) {
    const n = Number(p);
    return Number.isFinite(n) ? (n * 100).toFixed(1) + ' %' : esc(p);
}

// Carga un fichero de log en el textarea
inputFichero.addEventListener('change', function () {
    const fichero = inputFichero.files[0];
    if (!fichero) {
        return;
    }
    const lector = new FileReader();
    lector.onload = () => {
        textareaLog.value = lector.result;
    };
    lector.onerror = () => {
        mostrarError('<strong>No se pudo leer el fichero.</strong> Prueba a pegar el contenido directamente.');
    };
    lector.readAsText(fichero);
});

form.addEventListener('submit', async function (e) {
    e.preventDefault(); // Evitamos que la página se recargue
    limpiarPantalla();

    // 1. Leer los valores del formulario
    const textoLog = textareaLog.value;
    const umbralValor = parseFloat(document.getElementById('umbral').value);
    const textoListaBlanca = document.getElementById('lista-blanca').value;

    // 2. Validaciones básicas antes de llamar a la API
    // \r?\n para que también funcionen los ficheros con saltos de línea de Windows
    const lineasArray = textoLog.split(/\r?\n/).filter(linea => linea.trim() !== '');

    if (lineasArray.length === 0) {
        mostrarError('<strong>Falta el log.</strong> Pega al menos una línea o carga un fichero.');
        return;
    }
    if (lineasArray.length > LIMITE_LINEAS) {
        mostrarError(
            `<strong>Demasiadas líneas (${lineasArray.length}).</strong> ` +
            `La API admite como máximo ${LIMITE_LINEAS} líneas por petición.`
        );
        return;
    }
    if (Number.isNaN(umbralValor) || umbralValor < 0 || umbralValor > 1) {
        mostrarError('<strong>Umbral no válido.</strong> Debe ser un número entre 0 y 1.');
        return;
    }

    // Lista blanca: separamos por comas, quitamos espacios y descartamos vacíos
    const listaBlancaArray = textoListaBlanca
        .split(',')
        .map(ip => ip.trim())
        .filter(ip => ip !== '');

    // 3. Cuerpo de la petición, con el formato del contrato de la API
    const payload = {
        lineas: lineasArray,
        umbral: umbralValor,
        lista_blanca: listaBlancaArray
    };

    botonAnalizar.disabled = true;
    botonAnalizar.textContent = 'Analizando...';

    try {
        // 4. Petición POST a la API con fetch
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        let datosRespuesta;
        try {
            datosRespuesta = await response.json();
        } catch (errJson) {
            mostrarError(`<strong>Respuesta no válida (${response.status}).</strong> La API no devolvió JSON.`);
            return;
        }

        // 5. Errores de la API (por ejemplo 422)
        if (!response.ok) {
            let mensajeError = 'Error al procesar la petición.';
            if (datosRespuesta.detail) {
                if (typeof datosRespuesta.detail === 'string') {
                    mensajeError = datosRespuesta.detail;
                } else if (Array.isArray(datosRespuesta.detail)) {
                    mensajeError = datosRespuesta.detail
                        // La API devuelve una lista de textos; FastAPI por defecto, objetos con "msg"
                        .map(d => (typeof d === 'string' ? d : (d.msg || JSON.stringify(d))))
                        .join('\n');
                } else {
                    mensajeError = JSON.stringify(datosRespuesta.detail, null, 2);
                }
            }
            mostrarError(`<strong>Error (${response.status}):</strong> <pre>${esc(mensajeError)}</pre>`);
            return;
        }

        // 6. Respuesta correcta (200): pintamos los resultados
        const sospechosas = datosRespuesta.sospechosas || [];

        // La API las devuelve ordenadas por IP; mostramos primero las más sospechosas
        sospechosas.sort((a, b) => Number(b.probabilidad) - Number(a.probabilidad));

        let html = `
            <h3>Resultados del análisis</h3>
            <p><strong>Líneas ignoradas:</strong> ${esc(comoNumero(datosRespuesta.lineas_ignoradas))}</p>
            <p><strong>IPs analizadas:</strong> ${esc(comoNumero(datosRespuesta.ips_analizadas))}</p>
            <h4>IPs sospechosas detectadas: ${sospechosas.length}</h4>
        `;

        if (sospechosas.length === 0) {
            html += '<p>No se han encontrado IPs sospechosas con este umbral.</p>';
        } else {
            html += `
                <div class="tabla-scroll">
                    <table>
                        <thead>
                            <tr><th>IP</th><th>Probabilidad</th><th>Motivo</th></tr>
                        </thead>
                        <tbody>
            `;
            sospechosas.forEach(item => {
                // data-label lo usa el CSS para mostrar cada fila como tarjeta en el móvil
                html += `
                    <tr>
                        <td data-label="IP">${esc(item.ip)}</td>
                        <td class="prob" data-label="Probabilidad">${formatearProbabilidad(item.probabilidad)}</td>
                        <td data-label="Motivo">${esc(item.motivo)}</td>
                    </tr>
                `;
            });
            html += `
                        </tbody>
                    </table>
                </div>
            `;
        }

        divResultados.innerHTML = html;
        divResultados.hidden = false;

    } catch (error) {
        // Errores de red: API apagada o bloqueo por CORS
        console.error('Error de red:', error);
        mostrarError(
            '<strong>Error de conexión:</strong> no se pudo conectar con la API en ' +
            '<code>http://127.0.0.1:8000</code>. Comprueba que está arrancada con ' +
            '<code>uvicorn api.main:app</code> y que permite peticiones desde esta página (CORS).'
        );
    } finally {
        botonAnalizar.disabled = false;
        botonAnalizar.textContent = 'Analizar log';
    }
});
