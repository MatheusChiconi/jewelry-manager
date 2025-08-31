// Arquivo historico_remessas.js

document.addEventListener('DOMContentLoaded', function() {
    
    // Seleciona os elementos que serão animados
    const pageHeader = document.querySelector('.page-header');
    const filterCard = document.querySelector('.filter-card');
    const resultCards = document.querySelectorAll('.result-card');

    // 1. Anima o cabeçalho e o card de filtro
    if (pageHeader) {
        setTimeout(() => pageHeader.classList.add('visible'), 100);
    }
    if (filterCard) {
        setTimeout(() => filterCard.classList.add('visible'), 200);
    }

    // 2. Anima cada card de resultado com um atraso escalonado
    resultCards.forEach((card, index) => {
        setTimeout(() => {
            card.classList.add('visible');
        }, 300 + (100 * index)); 
    });

    // 3. Adiciona funcionalidade aos botões "Ver Detalhes"
    const verDetalhesButtons = document.querySelectorAll('.btn-ver-detalhes');
    
    verDetalhesButtons.forEach(button => {
        button.addEventListener('click', async function(e) {
            e.preventDefault();
            
            const remessaId = this.dataset.remessaId;
            
            // Desabilita o botão temporariamente
            const originalContent = this.innerHTML;
            this.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Gerando...';
            this.disabled = true;
            
            try {
                await imprimirReciboAntigo(remessaId);
            } catch (error) {
                alert(`Erro ao gerar recibo: ${error.message}`);
            } finally {
                // Restaura o botão
                this.innerHTML = originalContent;
                this.disabled = false;
            }
        });
    });

    // 4. Função para imprimir recibo antigo
    async function imprimirReciboAntigo(remessaId) {
        try {
            const response = await fetch('/clientes/imprimirReciboAntigo/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    remessaID: remessaId
                })
            });
            
            const data = await response.json();
            
            if (data.success && data.pdf_base64) {
                // Cria um link temporário para iniciar o download do PDF
                const link = document.createElement('a');
                link.href = 'data:application/pdf;base64,' + data.pdf_base64;
                link.download = data.nome_arquivo || `recibo_remessa_${remessaId}.pdf`;
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
            } else {
                throw new Error(data.error || 'Não foi possível gerar o PDF.');
            }
        } catch (error) {
            throw error;
        }
    }

    // 5. Função auxiliar para pegar o token CSRF
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

    console.log("Página de histórico de remessas carregada.");

});
