// Arquivo script.js

document.addEventListener('DOMContentLoaded', function() {
    
    // Seleciona os elementos que serão animados
    const stepHeader = document.querySelector('.step-header');
    const typeCards = document.querySelectorAll('.type-card');

    // 1. Anima o cabeçalho primeiro
    setTimeout(() => {
        stepHeader.classList.add('visible');
    }, 200); // Um pequeno atraso inicial

    // 2. Anima cada card de seleção com um atraso escalonado
    typeCards.forEach((card, index) => {
        // O atraso total inclui o tempo do cabeçalho para criar uma sequência
        setTimeout(() => {
            card.classList.add('visible');
        }, 400 + (150 * index)); 
    });

});
