// Arquivo selecionar_cadastro.js

document.addEventListener('DOMContentLoaded', function() {
    
    // Seleciona os elementos que serão animados
    const stepHeader = document.querySelector('.step-header');
    const selectionCards = document.querySelectorAll('.selection-card');
    const backLink = document.querySelector('.back-link-container');

    // 1. Anima o cabeçalho
    if (stepHeader) {
        setTimeout(() => {
            stepHeader.classList.add('visible');
        }, 70); // Um pequeno atraso inicial
    }

    // 2. Anima cada card de seleção com um atraso escalonado
    selectionCards.forEach((card, index) => {
        // O atraso total inclui o tempo do cabeçalho para criar uma sequência
        setTimeout(() => {
            card.classList.add('visible');
        }, 100 + (200 * index)); 
    });

    // 3. Anima o link de 'voltar' por último
    if (backLink) {
        setTimeout(() => {
            backLink.classList.add('visible');
        }, 600);
    }

    console.log("Página de seleção de cadastro carregada.");

});
