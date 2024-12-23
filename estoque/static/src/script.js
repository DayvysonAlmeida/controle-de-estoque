// Função para alternar a visibilidade do menu lateral
function toggleSidebar() {
    const sidebar = document.querySelector('.sidebar');
    const mainContent = document.querySelector('.main-content');
    sidebar.classList.toggle('hidden');
    mainContent.classList.toggle('expanded');
}

// Função para carregar os equipamentos dinamicamente
async function fetchEquipamentos() {
    try {
        const response = await fetch('/equipamentos/');
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        const equipamentos = await response.json();
        renderEquipamentos(equipamentos);
    } catch (error) {
        console.error('There was a problem with the fetch operation:', error);
    }
}

// Função para renderizar a lista de equipamentos
function renderEquipamentos(equipamentos) {
    const listContainer = document.querySelector('.equipamentos-list');
    listContainer.innerHTML = '';
    equipamentos.forEach(equipamento => {
        const listItem = document.createElement('li');
        listItem.textContent = equipamento.nome;
        listContainer.appendChild(listItem);
    });
}

document.addEventListener('DOMContentLoaded', fetchEquipamentos);
