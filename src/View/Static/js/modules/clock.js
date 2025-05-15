export function updateClock() {
    const now = new Date();
    document.getElementById('reloj').textContent = now.toLocaleString();
}