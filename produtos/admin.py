from django.contrib import admin
from .models import Produto, TipoPeca

@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tipo_peca', 'fornecedor', 'gramas', 'preco_venda', 'estoque', 'codigo_barras')
    list_filter = ('tipo_peca', 'fornecedor')
    search_fields = ('nome', 'codigo_barras', 'tipo_peca__nome', 'fornecedor__nome')
    list_per_page = 25
    readonly_fields = ('preco_venda',)

    fieldsets = (
        ('Informações Principais', {
            'fields': ('nome', 'tipo_peca', 'fornecedor', 'estoque')
        }),
        ('Cálculo por Peso (Ouro)', {
            'classes': ('secao-ouro',),
            'fields': ('gramas',)
        }),
        ('Cálculo por Custo (Folheado/Prata)', {
            'classes': ('secao-custo',),
            'fields': ('custo', 'margem_lucro')
        }),
        ('Resultados e Código', {
            'fields': ('preco_venda', 'codigo_barras')
        }),
    )

    class Media:
        js = ('produtos/js/admin_form_logica.js',)

@admin.register(TipoPeca)
class TipoPecaAdmin(admin.ModelAdmin):
    list_display = ['nome']
    search_fields = ['nome']
