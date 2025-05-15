export function updateStats(stats) {
    if (!stats) return;
    
    // Actualizar todos los contadores
    document.getElementById('totalRegistros').textContent = stats.total_registros || '--';
    document.getElementById('totalBloques').textContent = stats.total_bloques || '--';
    document.getElementById('registros24h').textContent = stats.registros_24h || '--';
    
    // Actualizar último registro
    if (stats.ultimo_registro) {
        document.getElementById('ultimoRegistroId').textContent = stats.ultimo_registro.id;
        document.getElementById('ultimoRegistroFecha').textContent = 
            new Date(stats.ultimo_registro.fecha_hora).toLocaleString();
        document.getElementById('ultimoRegistroHash').textContent = stats.ultimo_registro.hash;
    }
}

export function updateDailyStats(data) {
    const tbody = document.getElementById('estadisticasDiarias');
    tbody.innerHTML = data.map(row => `
        <tr>
            <td>${new Date(row.fecha).toLocaleDateString()}</td>
            <td>${row.total}</td>
        </tr>
    `).join('');
}

export function hideLoadingOverlay() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.style.display = 'none';
    }
}