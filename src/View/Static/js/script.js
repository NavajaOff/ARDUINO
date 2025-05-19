import { updateClock } from './modules/clock.js';
import { updateTrafficChart } from './modules/charts.js';
import { updateStats, updateDailyStats, hideLoadingOverlay, showLoadingOverlay } from './modules/ui.js';
import { updateBlocksTable, setupPagination } from './modules/blocks.js';

// Make functions globally accessible for onclick attributes
window.changePage = async function(page) {
    console.log(`Changing to page ${page}`);
    showLoadingOverlay();

    try {
        const response = await fetch(`/api/ultimos_bloques?page=${page}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        
        if (data.error) {
            console.error('Server error fetching blocks:', data.error);
            // Potentially show an alert here
        } else {
            updateBlocksTable(data);
            setupPagination(data.pagina_actual, data.total_paginas);
        }

    } catch (error) {
        console.error('Error fetching blocks:', error);
        // Potentially show an alert here
    } finally {
        hideLoadingOverlay();
    }
};

// Helper function to show alerts
function showAlert(message, type) {
    const alertDiv = document.getElementById('statusAlert');
    alertDiv.textContent = message;
    alertDiv.className = `alert alert-${type} d-block mb-4`;
}

// Helper function to hide alerts
function hideAlert() {
    const alertDiv = document.getElementById('statusAlert');
    alertDiv.className = 'alert d-none mb-4';
    alertDiv.textContent = '';
}

// Function to handle integrity check
async function verificarIntegridad() {
    console.log('Verifying blockchain integrity...');
    showLoadingOverlay();
    hideAlert(); // Hide previous alerts

    try {
        const response = await fetch('/api/verificar_integridad');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();

        if (data.integridad !== undefined) {
            if (data.integridad) {
                showAlert('Integridad de la blockchain verificada y válida.', 'success');
            } else {
                showAlert('La integridad de la blockchain NO es válida.', 'danger');
            }
        } else if (data.error) {
            showAlert(`Error al verificar integridad: ${data.error}`, 'danger');
        } else {
             showAlert('Respuesta inesperada del servidor al verificar integridad.', 'warning');
        }

    } catch (error) {
        console.error('Error verifying integrity:', error);
        showAlert(`Error de red al verificar integridad: ${error}`, 'danger');
    } finally {
        hideLoadingOverlay();
    }
}

// Make verificarIntegridad globally accessible
window.verificarIntegridad = verificarIntegridad;

function initializeSSE() {
    const eventSource = new EventSource('/events', { 
        withCredentials: true 
    });

    let lastUpdate = 0;
    const UPDATE_INTERVAL = 1000; // 1 segundo entre actualizaciones

    eventSource.onmessage = (event) => {
        try {
            const now = Date.now();
            const data = JSON.parse(event.data);
            
            // Check for errors
            if (data.error) {
                console.error('Server error:', data.error);
                return;
            }
            
            // Update UI components with rate limiting
            if (now - lastUpdate >= UPDATE_INTERVAL) {
                if (data.stats) updateStats(data.stats);
                if (data.trafico) updateTrafficChart(data.trafico);
                if (data.estadisticas) updateDailyStats(data.estadisticas);
                if (data.bloques) updateBlocksTable(data.bloques);
                lastUpdate = now;
            }
        } catch (error) {
            console.error('Error processing SSE update:', error);
        }
    };

    eventSource.onerror = (error) => {
        console.warn('SSE Connection lost. Attempting to reconnect...');
        if (eventSource.readyState === EventSource.CLOSED) {
            eventSource.close();
            setTimeout(() => {
                console.log('Reconnecting...');
                initializeSSE();
            }, 5000);
        }
    };

    eventSource.onopen = () => {
        console.log('SSE Connection established');
    };

    // Clean up on page unload
    window.addEventListener('beforeunload', () => {
        eventSource.close();
    });
}

document.addEventListener('DOMContentLoaded', async () => {
    try {
        // Initial load
        if (initialData.stats) updateStats(initialData.stats);
        if (initialData.trafico) updateTrafficChart(initialData.trafico);
        if (initialData.estadisticas) updateDailyStats(initialData.estadisticas);
        if (initialData.bloques) updateBlocksTable(initialData.bloques);

        // Setup clock
        updateClock();
        setInterval(updateClock, 1000);

        // Initialize SSE
        initializeSSE();

        hideLoadingOverlay();
    } catch (error) {
        console.error('Error:', error);
        hideLoadingOverlay();
    }
});