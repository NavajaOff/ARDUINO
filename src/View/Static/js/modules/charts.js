let trafficChart = null;  // Variable para mantener la referencia al gráfico

export function updateTrafficChart(data) {
    const ctx = document.getElementById('trafficChart').getContext('2d');
    
    if (!trafficChart) {
        // Crear el gráfico solo si no existe
        trafficChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: [],
                datasets: [{
                    label: 'Vehículos detectados',
                    data: [],
                    backgroundColor: 'rgba(54, 162, 235, 0.5)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                animation: {
                    duration: 0 // deshabilitar animación para actualizaciones más suaves
                },
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

    // Actualizar datos existentes
    trafficChart.data.labels = data.map(d => `${d.hora}:00`);
    trafficChart.data.datasets[0].data = data.map(d => d.cantidad);
    trafficChart.update('none'); // actualizar sin animación
}

// Función para limpiar el gráfico cuando sea necesario
export function destroyTrafficChart() {
    if (trafficChart) {
        trafficChart.destroy();
        trafficChart = null;
    }
}