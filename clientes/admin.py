from django.contrib import admin
from .models import Cliente, Remessa

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = (
        'nome_completo',
        'tipo_cliente_fornecedor',
        'cpf_cnpj',
        'telefone_whatsapp',
        'data_cadastro_formatada',
    )
    list_filter = ('fornecedor',)
    search_fields = ('nome_completo', 'cpf_cnpj')
    ordering = ['nome_completo']
    readonly_fields = ('data_cadastro',)

    def tipo_cliente_fornecedor(self, obj):
        return "Fornecedor" if obj.fornecedor else "Cliente"
    tipo_cliente_fornecedor.short_description = 'Tipo'

    def data_cadastro_formatada(self, obj):
        return obj.data_cadastro.strftime('%d/%m/%Y %H:%M')
    data_cadastro_formatada.short_description = 'Data de Cadastro'

class RemessaAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'cliente',
        'data_saida',
        'status',
    )
    list_filter = ('status',)
    search_fields = ('cliente__nome_completo',)
    ordering = ['-data_saida']
    readonly_fields = ('data_saida',)
admin.site.register(Remessa, RemessaAdmin)  
