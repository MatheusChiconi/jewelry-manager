document.addEventListener('DOMContentLoaded', function() {
    
    // --- LÓGICA PARA RESTAURAR O ÚLTIMO TIPO DA PEÇA SELECIONADO ---
    const selectTipo = document.getElementById("id_tipo_peca");

    const ultimoTipo = localStorage.getItem("ultimo_tipo_peca");
    if (ultimoTipo && selectTipo) {
        selectTipo.value = ultimoTipo;
    }

    selectTipo?.addEventListener("change", function () {
        localStorage.setItem("ultimo_tipo_peca", this.value);
    });

    // ----------- //

    // --- LÓGICA PARA RESTAURAR O ÚLTIMO FORNECEDOR SELECIONADO ---
    const selectFornecedor = document.getElementById("id_fornecedor");

    if (selectFornecedor) {
        const ultimoFornecedor = localStorage.getItem("ultimo_fornecedor");
        if (ultimoFornecedor) {
            selectFornecedor.value = ultimoFornecedor;
        }

        selectFornecedor.addEventListener("change", function () {
            localStorage.setItem("ultimo_fornecedor", this.value);
        });
    }
    // ----------- //

    // --- LÓGICA DE FOCO AUTOMÁTICO ---
    const nomeInput = document.getElementById('id_nome');
    if (nomeInput) {
        setTimeout(() => {
            nomeInput.focus();
        }, 80);
    }

    // --- LÓGICA DE ANIMAÇÃO DE ENTRADA ---
    const stepHeader = document.querySelector('.step-header');
    const formFields = document.querySelectorAll('.form-field');

    if (stepHeader) {
        setTimeout(() => {
            stepHeader.classList.add('visible');
        }, 25);
    }

    formFields.forEach((field, index) => {
        setTimeout(() => {
            field.classList.add('visible');
        }, 50 + (12.5 * index));
    });

    console.log("Formulário de cadastro carregado.");

    // --- FUNÇÃO PARA CÁLCULO DE PREÇO DE VENDA ---
    const custoInput = document.getElementById('id_custo');
    const margemInput = document.getElementById('id_margem_lucro');
    const vendaInput = document.getElementById('preco_venda');

    function calcularPrecoVenda() {
        const custoValor = parseFloat(custoInput.value.replace(',', '.')) || 0;
        const margemValor = parseFloat(margemInput.value.replace(',', '.')) || 0;

        if (custoValor > 0 && margemValor > 0) {
            const fatorMargem = 1 + (margemValor / 100);
            const precoFinal = custoValor * fatorMargem;
            const precoFormatado = precoFinal.toFixed(2).replace('.', ',');
            vendaInput.value = `R$ ${precoFormatado}`;
            console.log(`Cálculo realizado: Custo=${custoValor}, Margem=${margemValor}%, Preço Final=${precoFinal.toFixed(2)}`);
        } else {
            vendaInput.value = "Calculado automaticamente";
        }
    }

    function verificarEChamarCalculo() {
        if (custoInput && margemInput) {
            const custoPreenchido = custoInput.value.trim();
            const margemPreenchida = margemInput.value.trim();
            if (custoPreenchido && margemPreenchida) {
                calcularPrecoVenda();
            } else {
                vendaInput.value = "Calculado automaticamente";
            }
        }
    }

    if (custoInput && margemInput) {
        custoInput.addEventListener('input', verificarEChamarCalculo);
        margemInput.addEventListener('input', verificarEChamarCalculo);
    } else {
        console.error("Não foi possível encontrar os campos 'id_custo' ou 'id_margem_lucro'.");
    }

    // =================================================================
    // NOVA LÓGICA PARA NOTIFICAÇÕES E SONS
    // =================================================================
    const toastElement = document.querySelector('.toast');

    if (toastElement) {
        const toast = new bootstrap.Toast(toastElement, {
            delay: 3000
        });

        function playSuccessSound() {
            try {
                const audioContext = new (window.AudioContext || window.webkitAudioContext)();
                const oscillator = audioContext.createOscillator();
                const gainNode = audioContext.createGain();
                oscillator.connect(gainNode);
                gainNode.connect(audioContext.destination);
                oscillator.type = 'triangle';
                oscillator.frequency.setValueAtTime(1200, audioContext.currentTime);
                oscillator.frequency.exponentialRampToValueAtTime(600, audioContext.currentTime + 0.2);
                gainNode.gain.setValueAtTime(0.2, audioContext.currentTime);
                gainNode.gain.exponentialRampToValueAtTime(0.001, audioContext.currentTime + 0.3);
                oscillator.start(audioContext.currentTime);
                oscillator.stop(audioContext.currentTime + 0.3);
            } catch (e) {
                console.error("Não foi possível tocar o som de sucesso:", e);
            }
        }

        function playErrorSound() {
            try {
                const audioContext = new (window.AudioContext || window.webkitAudioContext)();
                const oscillator = audioContext.createOscillator();
                const gainNode = audioContext.createGain();
                oscillator.connect(gainNode);
                gainNode.connect(audioContext.destination);
                oscillator.type = 'sawtooth';
                oscillator.frequency.setValueAtTime(200, audioContext.currentTime);
                gainNode.gain.setValueAtTime(0.15, audioContext.currentTime);
                oscillator.start();
                oscillator.stop(audioContext.currentTime + 0.15);
            } catch (e) {
                console.error("Não foi possível tocar o som de erro:", e);
            }
        }

        // Verifica se a notificação é de sucesso (verde) ou erro (vermelha)
        if (toastElement.classList.contains('bg-success')) {
            playSuccessSound();
        } else if (toastElement.classList.contains('bg-danger')) {
            playErrorSound();
        }

        // Mostra a notificação na tela
        toast.show();
    }
});
