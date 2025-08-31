// Arquivo adicionar_cliente.js

document.addEventListener('DOMContentLoaded', function() {
    
    // --- LÓGICA DE FOCO AUTOMÁTICO ---
    const nomeCompletoInput = document.getElementById('id_nome_completo');
    if (nomeCompletoInput) {
        setTimeout(() => {
            nomeCompletoInput.focus();
        }, 450);
    }

    // --- LÓGICA DE ANIMAÇÃO DE ENTRADA ---
    const stepHeader = document.querySelector('.step-header');
    const formFields = document.querySelectorAll('.form-field');

    if (stepHeader) {
        setTimeout(() => {
            stepHeader.classList.add('visible');
        }, 100);
    }

    formFields.forEach((field, index) => {
        setTimeout(() => {
            field.classList.add('visible');
        }, 50 + (50 * index)); 
    });

    console.log("Página de cadastro de cliente carregada.");

    // =================================================================
    // LÓGICA PARA NOTIFICAÇÃO - CORRIGIDA
    // =================================================================

    const toastElement = document.querySelector('.toast');

    if (toastElement) {
        const toast = new bootstrap.Toast(toastElement, {
            delay: 3000
        });

        // Função para tocar o som de "PLIN" de sucesso
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

        // Função para tocar um som de erro, mais grave
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

        // AQUI ESTÁ A MUDANÇA: A lógica agora é explícita.
        // Só toca o som de sucesso se a notificação for verde.
        if (toastElement.classList.contains('bg-success')) {
            playSuccessSound();
        } else if (toastElement.classList.contains('bg-danger')) {
            playErrorSound();
        }

        // Mostra a notificação na tela
        toast.show();
    }
});
