function addPaginationControl(pagination, currentPage, totalPages) {
    // Botón Anterior
    const prevLi = document.createElement('li');
    prevLi.className = `page-item ${currentPage <= 1 ? 'disabled' : ''}`;
    prevLi.innerHTML = `
        <button class="page-link" ${currentPage <= 1 ? 'disabled' : ''} onclick="changePage(${currentPage - 1})">
            <i class="fas fa-chevron-left"></i>
        </button>
    `;
    pagination.appendChild(prevLi);
}

function addPageNumbers(pagination, currentPage, totalPages) {
    // Números de página
    for (let i = 1; i <= totalPages; i++) {
        if (
            i === 1 || 
            i === totalPages || 
            (i >= currentPage - 1 && i <= currentPage + 1)
        ) {
            const li = document.createElement('li');
            li.className = `page-item ${i === currentPage ? 'active' : ''}`;
            li.innerHTML = `
                <button class="page-link" onclick="changePage(${i})">${i}</button>
            `;
            pagination.appendChild(li);
        } else if (
            i === currentPage - 2 || 
            i === currentPage + 2
        ) {
            const li = document.createElement('li');
            li.className = 'page-item disabled';
            li.innerHTML = '<span class="page-link">...</span>';
            pagination.appendChild(li);
        }
    }
}

function addNextControl(pagination, currentPage, totalPages) {
    // Botón Siguiente
    const nextLi = document.createElement('li');
    nextLi.className = `page-item ${currentPage >= totalPages ? 'disabled' : ''}`;
    nextLi.innerHTML = `
        <button class="page-link" ${currentPage >= totalPages ? 'disabled' : ''} onclick="changePage(${currentPage + 1})">
            <i class="fas fa-chevron-right"></i>
        </button>
    `;
    pagination.appendChild(nextLi);
}

export function setupPagination(currentPage, totalPages) {
    const pagination = document.getElementById('bloquesPagination');
    pagination.innerHTML = '';

    addPaginationControl(pagination, currentPage, totalPages);
    addPageNumbers(pagination, currentPage, totalPages);
    addNextControl(pagination, currentPage, totalPages);
}

export function updateBlocksTable(data) {
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

    setupPagination(data.pagina_actual, data.total_paginas);
}