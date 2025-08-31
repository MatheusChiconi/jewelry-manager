document.addEventListener('DOMContentLoaded', function() {
    
    // --- 1. SELEÇÃO DOS ELEMENTOS DO DOM ---
    const searchForm = document.getElementById('search-form');
    const barcodeInput = document.getElementById('barcode-input');
    const productList = document.getElementById('product-list');
    const emptyMessage = document.getElementById('empty-list-message');
    const saveButton = document.getElementById('save-changes-btn');
    const feedbackMessage = document.getElementById('feedback-message');
    const productRowTemplate = document.getElementById('product-row-template');
    
    // Pega as URLs do Django que foram inseridas no HTML
    const urls = JSON.parse(document.getElementById('django-urls').textContent);

    // --- 2. FUNÇÃO PARA MOSTRAR FEEDBACK ANIMADO ---
    let feedbackTimeout;
    function showFeedback(message, type = 'danger') {
        feedbackMessage.textContent = message;
        // Adiciona classes para cor e para ativar a animação de fade-in
        feedbackMessage.className = `text-${type} feedback-message animated`;

        // Limpa qualquer timeout anterior para evitar que a mensagem suma antes da hora
        clearTimeout(feedbackTimeout);
        // Define um novo timeout para remover a mensagem após 3 segundos
        feedbackTimeout = setTimeout(() => {
            feedbackMessage.classList.remove('animated');
        }, 3000);
    }

    // --- 3. FUNÇÃO PARA BUSCAR PRODUTO NA API ---
    async function fetchProduct(barcode) {
        showFeedback('Buscando...', 'muted');

        try {
            const response = await fetch(`${urls.buscarProduto}?codigo=${barcode}`);
            const data = await response.json();

            if (data.status === 'success') {
                feedbackMessage.classList.remove('animated'); // Limpa a mensagem de "Buscando..."
                feedbackMessage.textContent = '';
                addProductToList(data.produto);
            } else {
                throw new Error(data.message);
            }
        } catch (error) {
            showFeedback(error.message, 'danger');
        }
    }

    // --- 4. FUNÇÃO PARA ADICIONAR PRODUTO À LISTA ---
    function addProductToList(produto) {
        if (document.querySelector(`.product-row[data-product-id="${produto.id}"]`)) {
            showFeedback('Este produto já está na lista.', 'warning');
            return;
        }

        const newRow = productRowTemplate.content.cloneNode(true).querySelector('.product-row');
        
        newRow.dataset.productId = produto.id;
        newRow.querySelector('.product-name').textContent = produto.nome;
        newRow.querySelector('.stock-current').textContent = produto.estoque_atual;
        const newStockInput = newRow.querySelector('.stock-new-input');
        newStockInput.value = produto.estoque_atual;

        // ANIMAÇÃO DE REMOÇÃO: Adiciona a classe de fade-out e remove o elemento no final da animação.
        newRow.querySelector('.remove-btn').addEventListener('click', () => {
            newRow.classList.add('fading-out');
            newRow.addEventListener('animationend', () => {
                newRow.remove();
                updateUIState();
            });
        });

        if (emptyMessage) emptyMessage.style.display = 'none';
        productList.prepend(newRow);
        newStockInput.focus();
        updateUIState();
    }

    // --- 5. FUNÇÃO PARA SALVAR AS ALTERAÇÕES ---
    async function saveStockChanges() {
        const productRows = productList.querySelectorAll('.product-row');
        const dataToSave = [];

        productRows.forEach(row => {
            dataToSave.push({
                id: row.dataset.productId,
                nova_quantidade: row.querySelector('.stock-new-input').value
            });
        });

        saveButton.disabled = true;
        saveButton.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Salvando...';

        try {
            const response = await fetch(urls.salvarEstoque, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({ produtos: dataToSave })
            });

            const result = await response.json();
            if (result.status === 'success') {
                window.location.reload(); 
            } else {
                throw new Error(result.message);
            }
        } catch (error) {
            alert(`Erro ao salvar: ${error.message}`);
            saveButton.disabled = false;
            saveButton.innerHTML = '<i class="fas fa-check me-2"></i>Salvar Alterações no Estoque';
        }
    }
    
    // --- 6. FUNÇÕES AUXILIARES E EVENT LISTENERS ---
    
    function updateUIState() {
        const hasItems = productList.querySelectorAll('.product-row').length > 0;
        if (emptyMessage) emptyMessage.style.display = hasItems ? 'none' : 'block';
        
        // ANIMAÇÃO DO BOTÃO SALVAR: Usa classes para controlar a visibilidade e animação.
        if (hasItems) {
            saveButton.style.display = 'block';
            setTimeout(() => saveButton.classList.add('visible'), 10);
        } else {
            saveButton.classList.remove('visible');
        }
    }

    searchForm.addEventListener('submit', function(event) {
        event.preventDefault();
        const barcode = barcodeInput.value.trim();
        if (barcode) {
            fetchProduct(barcode);
            barcodeInput.value = '';
        }
    });

    saveButton.addEventListener('click', saveStockChanges);

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    updateUIState();
});