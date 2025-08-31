from django.urls import path
from . import views

urlpatterns = [
    path('', views.produto_home, name='produto_home'),

    path('cadastrar/', views.produto_tipo, name='produto_tipo'),
    path('cadastrar/tipo/0', views.produto_cadastrar_folheado, name='produto_cadastrar_folheado'),
    path('cadastrar/tipo/1', views.produto_cadastrar_prata, name='produto_cadastrar_prata'),
    path('cadastrar/tipo/2', views.produto_cadastrar_ouro, name='produto_cadastrar_ouro'),

    path('editar-estoque/', views.pagina_edicao_estoque, name='produto_editar_estoque'),
    path('consultar/api/', views.buscar_produto_api, name='buscar_produto_api'),
    path('salvar/estoque/', views.salvar_estoque_api, name='salvar_estoque_api'),

    path('gerar-etiqueta/', views.gerar_etiqueta, name='gerar_etiqueta'),
    path('gerar-etiqueta/imprimir-etiquetas/', views.imprimir_etiquetas, name='imprimir_etiquetas'),


    path('consultar/', views.produto_consultar, name='produto_consultar'),
    path('produto/deletar/<int:produto_id>/', views.deletar_produto, name='deletar_produto'),
]