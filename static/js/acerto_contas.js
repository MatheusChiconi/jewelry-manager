document.addEventListener('DOMContentLoaded', function() {
    
    // --- 1. SELEÇÃO DOS ELEMENTOS DO DOM ---
    const remessaSearchModal = new bootstrap.Modal(document.getElementById('remessaSearchModal'));
    const remessaSearchInput = document.getElementById('remessa-search-input');
    const remessaSearchResults = document.getElementById('remessa-search-results');
    
    const initialView = document.getElementById('initial-view');
    const itemsView = document.getElementById('items-view');
    const remessaItemList = document.getElementById('remessa-item-list');
    
    const remessaSelectionArea = document.getElementById('remessa-selection-area');
    const remessaSelectedArea = document.getElementById('remessa-selected-area');
    const remessaClientName = document.getElementById('remessa-client-name');
    const remessaDate = document.getElementById('remessa-date');
    
    const scannerArea = document.getElementById('scanner-area');
    const scanProductForm = document.getElementById('scan-product-form');
    const barcodeInput = document.getElementById('barcode-input');
    const productFeedback = document.getElementById('product-feedback');
    
    const totalsHr = document.getElementById('totals-hr');
    const totalsSummary = document.getElementById('totals-summary');
    const totalItemsEl = document.getElementById('total-items');
    const totalPriceEl = document.getElementById('total-price');
    
    const finalActionArea = document.getElementById('final-action-area');
    const acaoFinalRadios = document.querySelectorAll('input[name="acao_final"]');
    const paymentMethodSection = document.getElementById('payment-method-section');
    const paymentMethodSelect = document.getElementById('payment-method-select');
    const finalizeAcertoBtn = document.getElementById('finalize-acerto-btn');
    
    const remessaItemTemplate = document.getElementById('remessa-item-template');
    const urls = JSON.parse(document.getElementById('django-urls').textContent);
    
    let currentRemessa = {
        id: null,
        items: [],
    };
    
    // --- CORREÇÃO: Adicionada verificação para depuração ---
    // Se o botão não for encontrado, um erro claro será exibido no console,
    // mas o resto do script não irá quebrar.
    if (!finalizeAcertoBtn) {
        console.error("ERRO DE INICIALIZAÇÃO: O botão com id 'finalize-acerto-btn' não foi encontrado no HTML. Verifique se o seu arquivo HTML corresponde à versão mais recente.");
    }
    // --- FIM DA CORREÇÃO ---

    acaoFinalRadios.forEach(radio => {
        radio.addEventListener('change', function() {
            if (this.value === 'FECHAR') {
                paymentMethodSection.classList.remove('d-none');
            } else {
                paymentMethodSection.classList.add('d-none');
            }
        });
    });

    // --- 2. LÓGICA DE BUSCA DE REMESSAS ---
    let searchTimeout;
    remessaSearchInput.addEventListener('input', () => {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(async () => {
            const query = remessaSearchInput.value.trim();
            const response = await fetch(`${urls.buscarRemessas}?q=${query}`);
            const data = await response.json();
            renderRemessaResults(data.remessas);
        }, 300);
    });

    function renderRemessaResults(remessas) {
        remessaSearchResults.innerHTML = '';
        if (remessas.length === 0) {
            remessaSearchResults.innerHTML = '<p class="text-center text-muted">Nenhuma remessa em aberto encontrada.</p>';
            return;
        }
        remessas.forEach(r => {
            const link = document.createElement('a');
            link.href = '#';
            link.className = 'list-group-item list-group-item-action';
            link.dataset.remessaId = r.id;
            link.innerHTML = `<div class="d-flex w-100 justify-content-between">
                                <h6 class="mb-1">${r.cliente_nome}</h6>
                                <small>${r.data_saida}</small>
                              </div>`;
            remessaSearchResults.appendChild(link);
        });
    }

    remessaSearchResults.addEventListener('click', (e) => {
        e.preventDefault();
        const selectedItem = e.target.closest('.list-group-item');
        if (selectedItem) {
            loadRemessaDetails(selectedItem.dataset.remessaId);
            remessaSearchModal.hide();
        }
    });

    // --- 3. LÓGICA PARA CARREGAR E EXIBIR DETALHES DA REMESSA ---
    async function loadRemessaDetails(remessaId) {
        const url = urls.detalhesRemessa.replace('0', remessaId);
        const response = await fetch(url);
        const data = await response.json();

        if (data.status === 'success') {
            currentRemessa.id = remessaId;
            currentRemessa.items = data.dados.itens;
            
            remessaClientName.textContent = data.dados.cliente_nome;
            remessaDate.textContent = data.dados.data_saida;
            
            remessaSelectionArea.classList.add('d-none');
            remessaSelectedArea.classList.remove('d-none');
            initialView.classList.add('d-none');
            itemsView.classList.remove('d-none');
            scannerArea.classList.remove('d-none');
            totalsHr.classList.remove('d-none');
            totalsSummary.classList.remove('d-none');
            finalActionArea.classList.remove('d-none');
            
            renderRemessaItems();
            updateTotalsAndButtons();
            barcodeInput.focus();
        } else {
            alert(data.message);
        }
    }

    function renderRemessaItems() {
        remessaItemList.innerHTML = '';
        currentRemessa.items.forEach(item => {
            const newRow = remessaItemTemplate.content.cloneNode(true).querySelector('.remessa-table-row');
            newRow.dataset.itemId = item.id;
            newRow.dataset.barcode = item.codigo_barras;
            newRow.querySelector('.product-name').textContent = item.produto_nome;
            newRow.querySelector('.product-code').textContent = `Cód: ${item.codigo_barras}`;
            newRow.querySelector('.product-quantity').textContent = item.quantidade;
            newRow.querySelector('.product-price').textContent = `R$ ${(item.quantidade * item.preco_unitario).toFixed(2)}`;
            remessaItemList.appendChild(newRow);
        });
    }

    // --- 4. LÓGICA PARA PROCESSAR PRODUTOS DEVOLVIDOS ---
    scanProductForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const barcode = barcodeInput.value.trim();
        if (!barcode) return;

        const itemRow = remessaItemList.querySelector(`tr[data-barcode="${barcode}"]`);

        if (itemRow && !itemRow.classList.contains('returned')) {
            const quantidadeCell = itemRow.querySelector('.product-quantity');
            const precoCell = itemRow.querySelector('.product-price');

            let quantidade = parseInt(quantidadeCell.textContent);
            const precoTotalAtual = parseFloat(precoCell.textContent.replace('R$', '').replace(',', '.'));
            const precoUnitario = precoTotalAtual / quantidade;

            if (quantidade > 1) {
                quantidade -= 1;
                quantidadeCell.textContent = quantidade;
                precoCell.textContent = `R$ ${(quantidade * precoUnitario).toFixed(2)}`;
                productFeedback.textContent = '1 unidade devolvida.';
                productFeedback.className = 'form-text text-warning';
                updateTotalsAndButtons();
            } else {
                itemRow.classList.add('removing');
                itemRow.addEventListener('animationend', () => {
                    itemRow.classList.remove('removing');
                    itemRow.classList.add('returned');
                    updateTotalsAndButtons();
                });
                productFeedback.textContent = 'Última unidade devolvida.';
                productFeedback.className = 'form-text text-success';
            }
        } else {
            productFeedback.textContent = 'Produto não encontrado nesta remessa ou já totalmente devolvido.';
            productFeedback.className = 'form-text text-danger';
        }

        barcodeInput.value = '';
    });

    // --- 5. LÓGICA DE ATUALIZAÇÃO DE TOTAIS ---
    function updateTotalsAndButtons() {
        let itemsToPay = 0;
        let priceToPay = 0;

        remessaItemList.querySelectorAll('tr.remessa-table-row:not(.returned)').forEach(row => {
            const quantidade = parseInt(row.querySelector('.product-quantity').textContent);
            const precoTexto = row.querySelector('.product-price').textContent;
            const precoTotal = parseFloat(precoTexto.replace('R$', '').replace(',', '.'));

            itemsToPay += quantidade;
            priceToPay += precoTotal;
        });

        totalItemsEl.textContent = itemsToPay;
        totalPriceEl.textContent = `R$ ${priceToPay.toFixed(2)}`;

        [totalItemsEl, totalPriceEl].forEach(el => {
            el.classList.add('highlight-total');
            setTimeout(() => el.classList.remove('highlight-total'), 300);
        });
        
        // --- CORREÇÃO: Adicionada verificação para não quebrar o script ---
        if (finalizeAcertoBtn) {
            finalizeAcertoBtn.disabled = false;
        }
        // --- FIM DA CORREÇÃO ---
    }


    // --- 6. LÓGICA PARA FINALIZAR O ACERTO ---
    async function finalizeAcerto() {
        const allItemRows = remessaItemList.querySelectorAll('tr.remessa-table-row');
    
        const itens = Array.from(allItemRows).map(row => {
            const id = row.dataset.itemId;
            const quantidade = row.classList.contains('returned')
                ? 0
                : parseInt(row.querySelector('.product-quantity').textContent);
            return { id, quantidade };
        });

        const acaoFinal = document.querySelector('input[name="acao_final"]:checked').value;

        const dataToSend = {
            remessa_id: currentRemessa.id,
            itens: itens, 
            acao_final: acaoFinal
        };

        if (acaoFinal === 'FECHAR') {
            dataToSend.forma_pagamento = paymentMethodSelect.value;
        }

        try {
            const response = await fetch(urls.finalizarAcerto, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify(dataToSend)
            });
            const result = await response.json();
            if (result.status === 'success') {
                alert(result.message);
                
                if (result.pdf_base64 && result.nome_arquivo) {
                    await baixarPDFAcerto(result.pdf_base64, result.nome_arquivo);
                } else if (result.pdf_error) {
                    console.warn('Erro na geração do PDF:', result.pdf_error);
                }
                
                window.location.reload();
            } else {
                throw new Error(result.message);
            }
        } catch (error) {
            alert(`Erro: ${error.message}`);
        }
    }

    async function baixarPDFAcerto(pdf_base64, nome_arquivo) {
        try {
            const link = document.createElement('a');
            link.href = 'data:application/pdf;base64,' + pdf_base64;
            link.download = nome_arquivo || 'acerto_remessa.pdf';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        } catch (error) {
            console.error('Erro ao baixar PDF de acerto:', error);
            alert('Acerto realizado com sucesso, mas houve erro ao baixar o recibo.');
        }
    }

    // --- CORREÇÃO: Adicionada verificação para não quebrar o script ---
    if (finalizeAcertoBtn) {
        finalizeAcertoBtn.addEventListener('click', finalizeAcerto);
    }
    // --- FIM DA CORREÇÃO ---

    // --- 7. FUNÇÃO AUXILIAR PARA PEGAR O TOKEN CSRF ---
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
