// Arquivo script.js

document.addEventListener('DOMContentLoaded', function() {
    
    // Seleciona todos os cards de ação que devem ser animados
    const actionCards = document.querySelectorAll('.action-card');

    // Itera sobre cada card e adiciona a classe 'visible' com um pequeno atraso.
    // Isso cria um efeito de cascata.
    actionCards.forEach((card, index) => {
        setTimeout(() => {
            card.classList.add('visible');
        }, 150 * (index + 1)); // Atraso de 150ms entre cada card
    });

});
