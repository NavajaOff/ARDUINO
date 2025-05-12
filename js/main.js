// Función para actualizar los datos cada 5 segundos
function actualizarDatos() {
    fetch('/api/stats')
        .then(response => response.json())
        .then(data => {
            document.getElementById('totalRegistros').textContent = data.total_registros;
            document.getElementById('totalBloques').textContent = data.total_bloques;
            document.getElementById('registros24h').textContent = data.registros_24h;
            
            if (data.ultimo_registro) {
                document.getElementById('ultimoRegistroId').textContent = data.ultimo_registro.id;
                document.getElementById('ultimoRegistroFecha').textContent = new Date(data.ultimo_registro.fecha_hora).toLocaleString();
                document.getElementById('ultimoRegistroHash').textContent = data.ultimo_registro.hash;
            }
            
            document.getElementById('integridadStatus').textContent = data.integridad ? 'Verificado' : 'Error';
            document.getElementById('integridadStatus').className = 'stat-value ' + (data.integridad ? 'text-success' : 'text-danger');
        })
        .catch(error => console.error('Error:', error));

    actualizarGraficoTrafico();
}

// Iniciar actualización automática
setInterval(actualizarDatos, 5000);
actualizarDatos(); // Primera actualización inmediata