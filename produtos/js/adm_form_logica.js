document.addEventListener('DOMContentLoaded', function() {
    (function($) {
        var tipoSelect = $('#id_tipo');
        var secaoOuro = $('.form-row.field-gramas').closest('fieldset');
        var secaoCusto = $('.form-row.field-custo').closest('fieldset');

        function atualizarVisibilidadeCampos() {
            var tipoSelecionado = tipoSelect.val();
            if (tipoSelecionado === 'OU') {
                secaoOuro.show();
                secaoCusto.hide();
            } else {
                secaoOuro.hide();
                secaoCusto.show();
            }
        }

        atualizarVisibilidadeCampos();

        tipoSelect.on('change', function() {
            atualizarVisibilidadeCampos();
        });

    })(django.jQuery);
});
