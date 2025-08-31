// Animações simples
document.addEventListener('DOMContentLoaded', function() {

    const metricCards = document.querySelectorAll('.metric-card');

    metricCards.forEach((card, index) => {
        setTimeout(() => {
            card.classList.add('animated');
        }, 150 * (index + 1));
    });
});
