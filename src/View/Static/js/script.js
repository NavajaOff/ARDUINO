// Variables globales
let trafficChart;
let currentBlockPage = 1;
let tiempoRealInterval = null;

// Mostrar fecha y hora actuales
function updateClock() {
    const now = new Date();
    document.getElementById('reloj').textContent = now.toLocaleString();
}

// Cargar estadísticas generales
async function loadStats() {
    try {
        const response = await fetch('/api/stats');
        const data = await response.json();

        updateStats(data);
    } catch (error) {
        console.error('Error al cargar estadísticas:', error);
        showAlert('Error al cargar estadísticas. Intente nuevamente.', 'danger');
    }
}

// Cargar datos de tráfico por hora
async function loadTrafficData() {
    try {
        const response = await fetch('/api/trafico_por_hora');
        const data = await response.json();

        updateTrafficChart(data);
    } catch (error) {
        console.error('Error al cargar datos de tráfico:', error);
        showAlert('Error al cargar datos de tráfico. Intente nuevamente.', 'danger');
    }
}

// Cargar estadísticas diarias
async function loadDailyStats() {
    try {
        const response = await fetch('/api/estadisticas_diarias');
        const data = await response.json();

        updateDailyStats(data);
    } catch (error) {
        console.error('Error al cargar estadísticas diarias:', error);
        showAlert('Error al cargar estadísticas diarias. Intente nuevamente.', 'danger');
    }
}

// Cargar bloques con paginación
async function loadBlocks(page = 1) {
    try {
        currentBlockPage = page;
        const response = await fetch(`/api/bloques?page=${page}&limit=10`);
        const data = await response.json();

        updateBlocksTable(data);
    } catch (error) {
        console.error('Error al cargar bloques:', error);
        showAlert('Error al cargar bloques. Intente nuevamente.', 'danger');
    }
}

// Configurar paginación
function setupPagination(currentPage, totalPages) {
    const pagination = document.getElementById('bloquesPagination');
    pagination.innerHTML = '';

    // Botón anterior
    const prevItem = document.createElement('li');
    prevItem.classList.add('page-item');
    if (currentPage === 1) prevItem.classList.add('disabled');

    const prevLink = document.createElement('a');
    prevLink.classList.add('page-link');
    prevLink.href = '#';
    prevLink.innerHTML = '&laquo;';
    prevLink.addEventListener('click', (e) => {
        e.preventDefault();
        if (currentPage > 1) loadBlocks(currentPage - 1);
    });

    prevItem.appendChild(prevLink);
    pagination.appendChild(prevItem);

    // Páginas
    const maxPages = 5;
    let startPage = Math.max(1, currentPage - Math.floor(maxPages / 2));
    let endPage = Math.min(totalPages, startPage + maxPages - 1);

    if (endPage - startPage + 1 < maxPages) {
        startPage = Math.max(1, endPage - maxPages + 1);
    }

    for (let i = startPage; i <= endPage; i++) {
        const pageItem = document.createElement('li');
        pageItem.classList.add('page-item');
        if (i === currentPage) pageItem.classList.add('active');

        const pageLink = document.createElement('a');
        pageLink.classList.add('page-link');
        pageLink.href = '#';
        pageLink.textContent = i;
        pageLink.addEventListener('click', (e) => {
            e.preventDefault();
            loadBlocks(i);
        });

        pageItem.appendChild(pageLink);
        pagination.appendChild(pageItem);
    }

    // Botón siguiente
    const nextItem = document.createElement('li');
    nextItem.classList.add('page-item');
    if (currentPage === totalPages) nextItem.classList.add('disabled');

    const nextLink = document.createElement('a');
    nextLink.classList.add('page-link');
    nextLink.href = '#';
    nextLink.innerHTML = '&raquo;';
    nextLink.addEventListener('click', (e) => {
        e.preventDefault();
        if (currentPage < totalPages) loadBlocks(currentPage + 1);
    });

    nextItem.appendChild(nextLink);
    pagination.appendChild(nextItem);
}

// Mostrar detalles del bloque
async function showBlockDetails(indice) {
    try {
        const response = await fetch(`/api/bloque/${indice}`);
        const data = await response.json();

        const bloque = data.bloque;

        // Actualizar campos del modal
        document.getElementById('modalBlockIndex').textContent = bloque.indice;
        document.getElementById('modalBlockHash').textContent = bloque.hash;
        document.getElementById('modalBlockPrevHash').textContent = bloque.hash_anterior;
        document.getElementById('modalBlockTime').textContent = bloque.fecha;
        document.getElementById('modalBlockNonce').textContent = bloque.nonce;

        // Mostrar datos en formato JSON
        let datosStr;
        if (typeof bloque.datos === 'object') {
            datosStr = JSON.stringify(bloque.datos, null, 2);
        } else {
            datosStr = bloque.datos;
        }
        document.getElementById('modalBlockData').textContent = datosStr;

        // Mostrar estado de integridad
        const statusDiv = document.getElementById('modalBlockStatus');
        if (data.es_valido) {
            statusDiv.innerHTML = `
                        <div class="alert alert-success">
                            <i class="fas fa-check-circle me-2"></i>
                            Este bloque es válido y mantiene la integridad de la cadena.
                        </div>
                    `;
        } else {
            statusDiv.innerHTML = `
                        <div class="alert alert-danger">
                            <i class="fas fa-exclamation-triangle me-2"></i>
                            ¡ALERTA! Este bloque no es válido. La integridad de la cadena puede estar comprometida.
                        </div>
                    `;
        }

        // Mostrar registros asociados
        const registrosTable = document.getElementById('modalBlockRegistros').querySelector('tbody');
        registrosTable.innerHTML = '';

        if (data.registros.length === 0) {
            const row = document.createElement('tr');
            row.innerHTML = '<td colspan="3" class="text-center">No hay registros asociados a este bloque</td>';
            registrosTable.appendChild(row);
        } else {
            data.registros.forEach(registro => {
                const row = document.createElement('tr');
                row.innerHTML = `
                            <td>${registro.id}</td>
                            <td>${new Date(registro.fecha_hora).toLocaleString()}</td>
                            <td><span class="hash-text">${registro.hash_bloque}</span></td>
                        `;
                registrosTable.appendChild(row);
            });
        }

        // Mostrar modal
        const modal = new bootstrap.Modal(document.getElementById('blockDetailModal'));
        modal.show();

        // Botón para copiar hash
        document.getElementById('copyBlockHash').addEventListener('click', () => {
            navigator.clipboard.writeText(bloque.hash)
                .then(() => {
                    alert('Hash copiado al portapapeles');
                })
                .catch(err => {
                    console.error('Error al copiar hash:', err);
                });
        });
    } catch (error) {
        console.error('Error al cargar detalles del bloque:', error);
        showAlert('Error al cargar detalles del bloque. Intente nuevamente.', 'danger');
    }
}

// Verificar integridad de la blockchain
async function checkIntegrity() {
    try {
        const response = await fetch('/api/verificar_integridad');
        const data = await response.json();

        // Mostrar mensaje de resultado
        if (data.integridad_ok) {
            showAlert('Verificación exitosa: La integridad de la blockchain está garantizada.', 'success');
        } else {
            showAlert('¡ALERTA! Se han detectado problemas de integridad en la blockchain.', 'danger');
        }
    } catch (error) {
        console.error('Error al verificar integridad:', error);
        showAlert('Error al verificar integridad. Intente nuevamente.', 'danger');
    }
}

// Mostrar alerta
function showAlert(message, type) {
    const alert = document.getElementById('statusAlert');
    alert.className = `alert alert-${type}`;
    alert.textContent = message;
    alert.classList.remove('d-none');

    // Ocultar alerta después de 5 segundos
    setTimeout(() => {
        alert.classList.add('d-none');
    }, 5000);
}

// Función para actualizar datos en tiempo real
async function actualizarDatosTiempoReal() {
    try {
        const response = await fetch('/api/datos_tiempo_real');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        
        if (data.error) {
            console.error('Error:', data.error);
            return;
        }

        // Actualizar último registro en la interfaz
        document.getElementById('ultimoRegistroId').textContent = data.id;
        document.getElementById('ultimoRegistroFecha').textContent = new Date(data.fecha_hora).toLocaleString();
        document.getElementById('ultimoRegistroHash').textContent = data.hash;
        
        // Actualizar contador de registros
        const totalRegistros = document.getElementById('totalRegistros');
        if (totalRegistros) {
            totalRegistros.textContent = parseInt(totalRegistros.textContent) + 1;
        }

        // Si hay un vehículo detectado, mostrar alerta
        if (data.estado === "VEHICULO DETECTADO") {
            showAlert(`¡Vehículo detectado! Distancia: ${data.distancia}cm`, 'success');
        }

    } catch (error) {
        console.error('Error al actualizar datos en tiempo real:', error);
        // Detener el intervalo si hay un error de conexión
        if (error.message.includes('Failed to fetch')) {
            if (tiempoRealInterval) {
                clearInterval(tiempoRealInterval);
                tiempoRealInterval = null;
                showAlert('Conexión perdida con el servidor. Recargue la página cuando el servidor esté disponible.', 'danger');
            }
        }
    }
}

// Inicializar aplicación
document.addEventListener('DOMContentLoaded', async () => {
    // Inicializar con datos del servidor
    if (initialData.stats) {
        updateStats(initialData.stats);
    }
    if (initialData.trafico) {
        updateTrafficChart(initialData.trafico);
    }
    if (initialData.estadisticas) {
        updateDailyStats(initialData.estadisticas);
    }
    if (initialData.bloques) {
        updateBlocksTable(initialData.bloques);
    }

    // Actualizar reloj
    updateClock();
    setInterval(updateClock, 1000);

    // Actualizar datos cada 5 segundos
    setInterval(loadAllData, 5000);

    // Iniciar intervalo solo si no está ya corriendo
    if (!tiempoRealInterval) {
        tiempoRealInterval = setInterval(actualizarDatosTiempoReal, 1000);
    }

    // Limpiar intervalo cuando la página se cierra o recarga
    window.addEventListener('beforeunload', () => {
        if (tiempoRealInterval) {
            clearInterval(tiempoRealInterval);
        }
    });
});

function updateStats(stats) {
    document.getElementById('totalRegistros').textContent = stats.total_registros;
    document.getElementById('totalBloques').textContent = stats.total_bloques;
    document.getElementById('registros24h').textContent = stats.registros_24h;
    document.getElementById('integridadStatus').textContent = stats.integridad ? 'Verificado' : 'Error';
    document.getElementById('integridadStatus').className = 'stat-value ' + (stats.integridad ? 'text-success' : 'text-danger');

    if (stats.ultimo_registro) {
        document.getElementById('ultimoRegistroId').textContent = stats.ultimo_registro.id;
        document.getElementById('ultimoRegistroFecha').textContent = new Date(stats.ultimo_registro.fecha_hora).toLocaleString();
        document.getElementById('ultimoRegistroHash').textContent = stats.ultimo_registro.hash;
    }
}

function updateTrafficChart(data) {
    const ctx = document.getElementById('trafficChart').getContext('2d');
    
    // Destruir el gráfico anterior si existe
    if (window.trafficChart instanceof Chart) {
        window.trafficChart.destroy();
    }

    // Crear nuevo gráfico
    window.trafficChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.map(d => `${d.hora}:00`),
            datasets: [{
                label: 'Vehículos detectados',
                data: data.map(d => d.cantidad),
                backgroundColor: 'rgba(54, 162, 235, 0.5)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            }
        }
    });
}

function updateDailyStats(data) {
    const tbody = document.getElementById('estadisticasDiarias');
    tbody.innerHTML = data.map(row => `
        <tr>
            <td>${new Date(row.fecha).toLocaleDateString()}</td>
            <td>${row.total}</td>
        </tr>
    `).join('');
}

function updateBlocksTable(data) {
    const tbody = document.getElementById('bloquesTable');
    tbody.innerHTML = data.bloques.map(bloque => `
        <tr>
            <td>${bloque.indice}</td>
            <td>${new Date(bloque.timestamp * 1000).toLocaleString()}</td>
            <td class="text-truncate" style="max-width: 150px;">${bloque.hash}</td>
            <td class="text-truncate" style="max-width: 150px;">${bloque.hash_anterior}</td>
            <td>${bloque.nonce}</td>
            <td>
                <button class="btn btn-sm btn-primary" onclick="showBlockDetails(${bloque.indice})">
                    <i class="fas fa-info-circle"></i>
                </button>
            </td>
        </tr>
    `).join('');

    // Actualizar paginación
    setupPagination(data.pagina_actual, data.total_paginas);
}

async function loadAllData() {
    try {
        const [stats, trafico, estadisticas, bloques] = await Promise.all([
            fetch('/api/stats').then(r => {
                if (!r.ok) throw new Error('Error en stats');
                return r.json();
            }),
            fetch('/api/trafico_por_hora').then(r => {
                if (!r.ok) throw new Error('Error en tráfico');
                return r.json();
            }),
            fetch('/api/estadisticas_diarias').then(r => {
                if (!r.ok) throw new Error('Error en estadísticas');
                return r.json();
            }),
            fetch('/api/ultimos_bloques').then(r => {
                if (!r.ok) throw new Error('Error en bloques');
                return r.json();
            })
        ]);

        updateStats(stats);
        updateTrafficChart(trafico);
        updateDailyStats(estadisticas);
        updateBlocksTable(bloques);
    } catch (error) {
        console.error('Error loading data:', error);
        showAlert('Error de conexión con el servidor', 'danger');
    }
}