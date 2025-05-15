
export async function fetchStats() {
    const response = await fetch('/api/stats');
    return await response.json();
}

export async function fetchTrafficData() {
    const response = await fetch('/api/trafico_por_hora');
    return await response.json();
}

export async function fetchDailyStats() {
    const response = await fetch('/api/estadisticas_diarias');
    return await response.json();
}

export async function fetchBlocks(page = 1) {
    const response = await fetch(`/api/bloques?page=${page}&limit=10`);
    return await response.json();
}

export async function fetchBlockDetails(indice) {
    const response = await fetch(`/api/bloque/${indice}`);
    return await response.json();
}

export async function checkIntegrity() {
    const response = await fetch('/api/verificar_integridad');
    return await response.json();
}