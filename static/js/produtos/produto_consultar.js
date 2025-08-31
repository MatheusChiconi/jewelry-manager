// Arquivo produto_consultar.js

document.addEventListener('DOMContentLoaded', function() {
    
    // --- LÓGICA DE ANIMAÇÃO DE ENTRADA (EXISTENTE) ---
    const pageHeader = document.querySelector('.page-header');
    const filterCard = document.querySelector('.filter-card');
    const tableContainer = document.querySelector('.table-container');
    const elementsToAnimate = [pageHeader, filterCard, tableContainer];

    elementsToAnimate.forEach((element, index) => {
        if (element) {
            setTimeout(() => {
                element.classList.add('visible');
            }, 50 * (index + 1));
        }
    });

    // --- NOVA LÓGICA PARA CONFIRMAÇÃO DE EXCLUSÃO ---

    // 1. Seleciona todos os botões que têm a classe '.btn-delete'.
    const deleteButtons = document.querySelectorAll('.btn-delete');

    // 2. Itera sobre cada botão encontrado.
    deleteButtons.forEach(button => {
        // 3. Adiciona um "escutador de eventos" que será acionado no clique.
        button.addEventListener('click', function(event) {
            
            // 4. Previne que o formulário seja enviado imediatamente.
            event.preventDefault();

            // 5. Exibe a caixa de diálogo de confirmação padrão do navegador.
            // A mensagem pode ser personalizada.
            const userConfirmed = window.confirm("Tem certeza que deseja excluir este produto? Esta ação não pode ser desfeita.");

            // 6. Verifica a resposta do usuário.
            if (userConfirmed) {
                // Se o usuário clicou em "OK", encontra o formulário pai do botão
                // e o envia para o servidor.
                // 'this.closest("form")' é uma forma segura de encontrar o formulário correto.
                this.closest('form').submit();
            }
            // Se o usuário clicou em "Cancelar", nada acontece.
        });
    });

    console.log("Página de inventário carregada e confirmação de exclusão ativada.");
});
