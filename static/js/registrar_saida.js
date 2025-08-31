document.addEventListener('DOMContentLoaded', function() {
    
    // --- 1. SELEÇÃO DOS ELEMENTOS DO DOM ---
    const barcodeInput = document.getElementById('barcode-input');
    const searchProductForm = document.getElementById('search-product-form');
    const productListBody = document.getElementById('product-list');
    const productFeedback = document.getElementById('product-feedback');
    
    const clientSearchModal = new bootstrap.Modal(document.getElementById('clientSearchModal'));
    const clientSearchInput = document.getElementById('client-search-input');
    const clientSearchResults = document.getElementById('client-search-results');
    
    const clientSelectionArea = document.getElementById('client-selection-area');
    const clientSelectedArea = document.getElementById('client-selected-area');
    const clientNameDisplay = document.getElementById('client-name-display');
    const changeClientBtn = document.getElementById('change-client-btn');

    const totalItemsEl = document.getElementById('total-items');
    const totalPriceEl = document.getElementById('total-price');
    const finalizeBtn = document.getElementById('finalize-btn');
    
    const productRowTemplate = document.getElementById('product-row-template');
    const clientResultTemplate = document.getElementById('client-result-template');
    
    const urls = JSON.parse(document.getElementById('django-urls').textContent);
    
    // --- MODIFICAÇÃO: Seleção dos novos elementos ---
    const tipoRemessaRadios = document.querySelectorAll('input[name="tipo_remessa"]');
    const paymentMethodSection = document.getElementById('payment-method-section');
    const paymentMethodSelect = document.getElementById('payment-method-select');
    // --- FIM DA MODIFICAÇÃO ---

    let selectedClientId = null;
    let productsInList = new Map(); // Usaremos um Map para gerenciar os produtos

    // --- MODIFICAÇÃO: Lógica para mostrar/esconder a seção de forma de pagamento ---
    tipoRemessaRadios.forEach(radio => {
        radio.addEventListener('change', () => {
            // Verifica se o radio 'VENDA' está marcado
            if (document.getElementById('tipo-venda').checked) {
                paymentMethodSection.classList.remove('d-none'); // Mostra a seção
            } else {
                paymentMethodSection.classList.add('d-none'); // Esconde a seção
            }
        });
    });
    // --- FIM DA MODIFICAÇÃO ---

    // --- 2. LÓGICA DE BUSCA DE CLIENTES ---
    let searchTimeout;
    clientSearchInput.addEventListener('input', () => {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(async () => {
            const query = clientSearchInput.value.trim();
            if (query.length < 2) {
                clientSearchResults.innerHTML = '';
                return;
            }
            const response = await fetch(`${urls.buscarClientes}?q=${query}`);
            const data = await response.json();
            renderClientResults(data.clientes);
        }, 300); // Atraso para não buscar a cada tecla digitada
    });

    function renderClientResults(clients) {
        clientSearchResults.innerHTML = '';
        if (clients.length === 0) {
            clientSearchResults.innerHTML = '<p class="text-center text-muted">Nenhum cliente encontrado.</p>';
            return;
        }
        clients.forEach(client => {
            const clientRow = clientResultTemplate.content.cloneNode(true).querySelector('.client-result-item');
            clientRow.dataset.clientId = client.id;
            clientRow.querySelector('.client-name').textContent = client.nome;
            clientRow.querySelector('.client-doc').textContent = `Documento: ${client.doc}`;
            clientSearchResults.appendChild(clientRow);
        });
    }

    clientSearchResults.addEventListener('click', (e) => {
        e.preventDefault();
        const selectedItem = e.target.closest('.client-result-item');
        if (selectedItem) {
            selectedClientId = selectedItem.dataset.clientId;
            clientNameDisplay.textContent = selectedItem.querySelector('.client-name').textContent;
            clientSelectionArea.classList.add('d-none');
            clientSelectedArea.classList.remove('d-none');
            clientSearchModal.hide();
            updateTotalsAndButton();
        }
    });

    changeClientBtn.addEventListener('click', () => {
        selectedClientId = null;
        clientSelectedArea.classList.add('d-none');
        clientSelectionArea.classList.remove('d-none');
        updateTotalsAndButton();
    });

    // --- 3. LÓGICA DE BUSCA E ADIÇÃO DE PRODUTOS ---
    searchProductForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const barcode = barcodeInput.value.trim();
        if (!barcode) return;

        try {
            const response = await fetch(`${urls.buscarProduto}?codigo=${barcode}`);
            const data = await response.json();
            if (data.status === 'success') {
                addProductToList(data.produto);
                productFeedback.textContent = '';
            } else {
                throw new Error(data.message);
            }
        } catch (error) {
            productFeedback.textContent = error.message;
            productFeedback.className = 'form-text text-danger';
        } finally {
            barcodeInput.value = '';
        }
    });

    function addProductToList(product) {
        if (productsInList.has(product.id)) {
            // Se o produto já está na lista, apenas incrementa a quantidade
            const existingRow = productsInList.get(product.id);
            const quantityInput = existingRow.querySelector('.product-quantity');
            quantityInput.value = parseInt(quantityInput.value) + 1;
            quantityInput.dispatchEvent(new Event('input')); // Dispara o evento para atualizar o subtotal
        } else {
            // Se é um produto novo, cria a linha na tabela
            const newRow = productRowTemplate.content.cloneNode(true).querySelector('.product-table-row');
            newRow.dataset.productId = product.id;
            newRow.dataset.price = product.preco_venda;
            newRow.querySelector('.product-name').textContent = product.nome;
            newRow.querySelector('.product-price').textContent = `R$ ${parseFloat(product.preco_venda).toFixed(2)}`;
            
            const quantityInput = newRow.querySelector('.product-quantity');
            quantityInput.addEventListener('input', updateTotalsAndButton);
            
            newRow.querySelector('.remove-product-btn').addEventListener('click', () => {
                productsInList.delete(product.id);
                newRow.remove();
                updateTotalsAndButton();
            });

            productListBody.prepend(newRow);
            productsInList.set(product.id, newRow);
            newRow.classList.add('new-item');
        }
        updateTotalsAndButton();
    }

    // --- 4. LÓGICA DE ATUALIZAÇÃO DE TOTAIS ---
    function updateTotalsAndButton() {
        let totalItems = 0;
        let totalPrice = 0;

        productsInList.forEach(row => {
            const quantity = parseInt(row.querySelector('.product-quantity').value) || 0;
            const price = parseFloat(row.dataset.price) || 0;
            const subtotal = quantity * price;

            totalItems += quantity;
            totalPrice += subtotal;

            row.querySelector('.product-subtotal').textContent = `R$ ${subtotal.toFixed(2)}`;
        });

        totalItemsEl.textContent = totalItems;
        totalPriceEl.textContent = `R$ ${totalPrice.toFixed(2)}`;
        
        // Habilita o botão de finalizar apenas se houver um cliente e produtos na lista
        finalizeBtn.disabled = !(selectedClientId && productsInList.size > 0);
    }

    // --- 5. LÓGICA PARA FINALIZAR A SAÍDA ---
    async function gerarReciboPDF(dadosRecibo) {
        try {
            const response = await fetch('/gerar_recibo_pdf/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify(dadosRecibo)
            });
            const data = await response.json();

            if (data.success && data.pdf_base64) {
                const link = document.createElement('a');
                link.href = 'data:application/pdf;base64,' + data.pdf_base64;
                link.download = data.nome_arquivo || 'recibo.pdf';
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
            } else {
                throw new Error(data.error || 'Não foi possível gerar o PDF.');
            }
        } catch (error) {
            alert(`A operação foi salva com sucesso, mas houve um erro ao gerar o recibo: ${error.message}`);
        }
    }

    finalizeBtn.addEventListener('click', async () => {
        if (!confirm('Deseja realmente finalizar esta operação?')) return;

        // --- COLETA DE DADOS ---
        const tipoRemessa = document.querySelector('input[name="tipo_remessa"]:checked').value;
        const nomeCliente = clientNameDisplay.textContent;

        const produtosParaRecibo = Array.from(productsInList.values()).map(row => ({
            nome: row.querySelector('.product-name').textContent,
            quantidade: row.querySelector('.product-quantity').value,
            preco_unitario: parseFloat(row.dataset.price).toFixed(2),
            subtotal: (parseFloat(row.dataset.price) * parseInt(row.querySelector('.product-quantity').value)).toFixed(2)
        }));
        
        const remessaData = {
            cliente_id: selectedClientId,
            tipo_remessa: tipoRemessa,
            produtos: Array.from(productsInList.values()).map(row => ({
                id: row.dataset.productId,
                quantidade: row.querySelector('.product-quantity').value
            }))
        };
        
        // Adiciona a forma de pagamento ao JSON se for 'VENDA' ---
        if (tipoRemessa === 'VENDA') {
            remessaData.forma_pagamento = paymentMethodSelect.value;
        }
        
        finalizeBtn.disabled = true;
        finalizeBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Finalizando...';

        try {
            const response = await fetch(urls.salvarRemessa, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify(remessaData)
            });
            const result = await response.json();
            const remessaID = result.id;

            if (result.status === 'success') {
                alert(result.message);

                const dadosRecibo = {
                    produtos: produtosParaRecibo,
                    nome_cliente: nomeCliente,
                    total_itens: totalItemsEl.textContent,
                    valor_total: totalPriceEl.textContent,
                    remessaID: remessaID,
                    tipoRemessa: tipoRemessa,
                };

                // Adiciona a forma de pagamento aos dados do recibo ---
                if (tipoRemessa === 'VENDA') {
                    dadosRecibo.forma_pagamento = paymentMethodSelect.options[paymentMethodSelect.selectedIndex].text;
                }

                await gerarReciboPDF(dadosRecibo);

                window.location.href = '/'; 

            } else {
                throw new Error(result.message);
            }
        } catch (error) {
            alert(`Erro ao finalizar: ${error.message}`);
            finalizeBtn.disabled = false;
            finalizeBtn.innerHTML = '<i class="fas fa-check-circle me-2"></i>Finalizar Saída';
        }
    });

    // --- 6. FUNÇÃO AUXILIAR PARA PEGAR O TOKEN CSRF ---
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
});
