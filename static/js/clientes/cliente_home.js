window.addEventListener("load", () => {
    const cards = document.querySelectorAll(".menu-card");

    cards.forEach((card) => {
        // Estado inicial (invisível e deslocado)
        card.style.opacity = "0";
        card.style.transform = "translateY(30px)";
        card.style.transition = "opacity 0.6s ease, transform 0.6s ease";
    });

    // Aplicar animação a todos após pequeno delay
    setTimeout(() => {
        cards.forEach((card) => {
            card.style.opacity = "1";
            card.style.transform = "translateY(0)";
        });
    }, 180);  // Delay geral de segurança
});
