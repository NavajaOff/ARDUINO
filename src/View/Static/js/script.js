// Variables globales
let trafficChart;
let currentBlockPage = 1;

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

        // Actualizar estadísticas
        document.getElementById('totalRegistros').textContent = data.total_registros;
        document.getElementById('totalBloques').textContent = data.total_bloques;
        document.getElementById('registros24h').textContent = data.registros_24h;

        // Mostrar estado de integridad
        const integridadStatus = document.getElementById('integridadStatus');
        if (data.integridad) {
            integridadStatus.textContent = 'Verificada';
            integridadStatus.classList.add('text-success');
        } else {
            integridadStatus.textContent = 'Comprometida';
            integridadStatus.classList.add('text-danger');
        }

        // Actualizar último registro
        if (data.ultimo_registro) {
            document.getElementById('ultimoRegistroId').textContent = data.ultimo_registro.id;
            document.getElementById('ultimoRegistroFecha').textContent = new Date(data.ultimo_registro.fecha_hora).toLocaleString();
            document.getElementById('ultimoRegistroHash').textContent = data.ultimo_registro.hash_bloque;
        }
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

        // Preparar datos para gráfico
        const labels = data.map(item => `${item.hora}:00`);
        const values = data.map(item => item.cantidad);

        // Crear gráfico
        const ctx = document.getElementById('trafficChart').getContext('2d');
        if (trafficChart) {
            trafficChart.destroy();
        }

        trafficChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Vehículos',
                    data: values,
                    backgroundColor: 'rgba(54, 162, 235, 0.2)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 2,
                    tension: 0.4,
                    pointRadius: 4,
                    pointBackgroundColor: 'rgba(54, 162, 235, 1)'
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            precision: 0
                        }
                    }
                }
            }
        });
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

        const tbody = document.getElementById('estadisticasDiarias');
        tbody.innerHTML = '';

        if (data.length === 0) {
            const row = document.createElement('tr');
            row.innerHTML = '<td colspan="2" class="text-center">No hay datos disponibles</td>';
            tbody.appendChild(row);
            return;
        }

        // Crear filas con datos
        data.forEach(item => {
            const row = document.createElement('tr');
            const date = new Date(item.fecha).toLocaleDateString();

            row.innerHTML = `
                        <td>${date}</td>
                        <td>${item.cantidad}</td>
                    `;
            tbody.appendChild(row);
        });
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

        const tbody = document.getElementById('bloquesTable');
        tbody.innerHTML = '';

        if (data.bloques.length === 0) {
            const row = document.createElement('tr');
            row.innerHTML = '<td colspan="6" class="text-center">No hay bloques disponibles</td>';
            tbody.appendChild(row);
            return;
        }

        // Crear filas con datos de bloques
        data.bloques.forEach(bloque => {
            const row = document.createElement('tr');

            row.innerHTML = `
                        <td>${bloque.indice}</td>
                        <td>${bloque.fecha}</td>
                        <td><span class="hash-text">${bloque.hash}</span></td>
                        <td><span class="hash-text">${bloque.hash_anterior}</span></td>
                        <td>${bloque.nonce}</td>
                        <td>
                            <button class="btn btn-sm btn-primary view-block" data-indice="${bloque.indice}">
                                <i class="fas fa-eye"></i>
                            </button>
                        </td>
                    `;
            tbody.appendChild(row);
        });

        // Configurar paginación
        setupPagination(data.page, data.pages);

        // Asignar eventos a botones de ver detalles
        document.querySelectorAll('.view-block').forEach(button => {
            button.addEventListener('click', () => {
                const indice = button.getAttribute('data-indice');
                showBlockDetails(indice);
            });
        });
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

// Inicializar aplicación
document.addEventListener('DOMContentLoaded', async () => {
    // Configurar reloj
    updateClock();
    setInterval(updateClock, 1000);

    try {
        // Cargar datos iniciales
        await Promise.all([
            loadStats(),
            loadTrafficData(),
            loadDailyStats(),
            loadBlocks()
        ]);

        // Ocultar overlay de carga
        document.getElementById('loadingOverlay').style.display = 'none';

        // Configurar botón para verificar integridad
        document.getElementById('verificarIntegridad').addEventListener('click', (e) => {
            e.preventDefault();
            checkIntegrity();
        });

        // Botón para copiar hash del último registro
        document.getElementById('copyLastHash').addEventListener('click', () => {
            const hash = document.getElementById('ultimoRegistroHash').textContent;
            navigator.clipboard.writeText(hash)
                .then(() => {
                    alert('Hash copiado al portapapeles');
                })
                .catch(err => {
                    console.error('Error al copiar hash:', err);
                });
        });

        // Actualizar datos cada 30 segundos
        setInterval(() => {
            loadStats();
            loadTrafficData();
            loadDailyStats();
            loadBlocks(currentBlockPage);
        }, 30000);

    } catch (error) {
        console.error('Error al inicializar la aplicación:', error);
        document.getElementById('loadingOverlay').style.display = 'none';
        showAlert('Error al cargar la aplicación. Intente recargar la página.', 'danger');
    }
});