// Arquivo consultar_clientes.js

document.addEventListener('DOMContentLoaded', function() {
    
    // Seleciona os elementos que serão animados
    const pageHeader = document.querySelector('.page-header');
    const filterCard = document.querySelector('.filter-card');
    const resultCards = document.querySelectorAll('.result-card');

    // 1. Anima o cabeçalho e o card de filtro
    if (pageHeader) {
        setTimeout(() => pageHeader.classList.add('visible'), 100);
    }
    if (filterCard) {
        setTimeout(() => filterCard.classList.add('visible'), 200);
    }

    // 2. Anima cada card de resultado com um atraso escalonado
    resultCards.forEach((card, index) => {
        setTimeout(() => {
            card.classList.add('visible');
        }, 300 + (100 * index)); 
    });

    console.log("Página de consulta de clientes e fornecedores carregada.");

});
