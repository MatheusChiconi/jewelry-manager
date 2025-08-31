document.addEventListener('DOMContentLoaded', function() {

    // --- 1. SELEÇÃO DOS ELEMENTOS DO DOM ---
    const searchInput = document.getElementById('search-product-input');
    const availableProductsList = document.getElementById('available-products-list');
    const allProductItems = availableProductsList.querySelectorAll('.product-item');
    
    const printQueueList = document.getElementById('print-queue-list');
    const emptyQueueMessage = document.getElementById('empty-queue-message');
    const queueItemTemplate = document.getElementById('print-queue-item-template');
    
    const generatePdfBtn = document.getElementById('generate-pdf-btn');
    // As variáveis para as opções de etiqueta foram removidas

    // --- 2. LÓGICA DA BUSCA DE PRODUTOS (FRONTEND) ---
    searchInput.addEventListener('input', function() {
        const searchTerm = this.value.toLowerCase().trim();

        allProductItems.forEach(item => {
            const productName = item.dataset.nome.toLowerCase();
            const productCode = item.dataset.codigo ? item.dataset.codigo.toLowerCase() : '';

            if (productName.includes(searchTerm) || productCode.includes(searchTerm)) {
                item.style.display = 'block';
            } else {
                item.style.display = 'none';
            }
        });
    });

    // --- 3. LÓGICA PARA ADICIONAR PRODUTO À FILA ---
    availableProductsList.addEventListener('click', function(event) {
        if (event.target.classList.contains('add-to-queue-btn')) {
            const productItem = event.target.closest('.product-item');
            const productId = productItem.dataset.id;
            const productName = productItem.dataset.nome;
            const productCode = productItem.dataset.codigo; // Pega o código do produto

            if (printQueueList.querySelector(`[data-id="${productId}"]`)) {
                alert('Este produto já está na fila de impressão.');
                return;
            }

            const newItem = queueItemTemplate.content.cloneNode(true).querySelector('.print-queue-item');
            
            // Preenche os dados do novo item
            newItem.dataset.id = productId;
            newItem.querySelector('.item-name').textContent = productName;
            newItem.querySelector('.item-code').textContent = `Cód: ${productCode || '-'}`;

            newItem.querySelector('.remove-from-queue-btn').addEventListener('click', handleRemoveItem);

            printQueueList.appendChild(newItem);
            updateQueueState();
        }
    });

    // --- 4. LÓGICA PARA REMOVER ITEM DA FILA ---
    function handleRemoveItem(event) {
        const itemToRemove = event.target.closest('.print-queue-item');
        itemToRemove.classList.add('removing');
        itemToRemove.addEventListener('animationend', () => {
            itemToRemove.remove();
            updateQueueState();
        });
    }

    // --- 5. LÓGICA PARA GERAR O ARQUIVO (ATUALIZADA) ---
    generatePdfBtn.addEventListener('click', function() {
        const itemsToPrint = [];
        const queueItems = printQueueList.querySelectorAll('.print-queue-item');

        if (queueItems.length === 0) {
            alert('A fila de impressão está vazia. Adicione produtos para gerar as etiquetas.');
            return;
        }

        queueItems.forEach(item => {
            itemsToPrint.push({
                id: item.dataset.id,
                quantidade: parseInt(item.querySelector('.item-quantity').value)
            });
        });

        // A lógica das opções foi removida
        
        fetch('imprimir-etiquetas/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': CSRFTOKEN // A variável CSRFTOKEN é definida no template
            },
            // O corpo do request agora envia apenas os produtos
            body: JSON.stringify({
                produtos: itemsToPrint
            })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error("Erro ao gerar etiquetas.");
            }
            return response.blob();
        })
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'etiquetas.pdf'; // Nome do arquivo alterado para .prn
            document.body.appendChild(a);
            a.click();
            a.remove();
        })
        .catch(error => {
            alert("Erro: " + error.message);
            console.error(error);
        });
    });

    // --- 6. FUNÇÃO AUXILIAR PARA ATUALIZAR A INTERFACE ---
    function updateQueueState() {
        const hasItems = printQueueList.querySelectorAll('.print-queue-item').length > 0;
        emptyQueueMessage.style.display = hasItems ? 'none' : 'block';
    }

});
