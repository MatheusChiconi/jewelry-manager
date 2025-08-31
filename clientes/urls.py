from django.urls import path
from . import views

urlpatterns = [
    # clientes/urls.py
    path('', views.cliente_home, name='cliente_home'),

    path('selecionarCadastro/', views.cliente_selecionarCadastro, name='cliente_selecionarCadastro'),
    path('cadastrarFornecedor/', views.cliente_cadastrarFornecedor, name='cliente_cadastrarFornecedor'),
    path('cadastrarCliente/', views.cliente_cadastrarCliente, name='cliente_cadastrarCliente'),
    path('consultar/', views.cliente_consultar, name='cliente_consultar'),
    path('historicoRemessa/', views.cliente_historicoRemessa, name='cliente_historicoRemessa'),
    path('imprimirReciboAntigo/', views.imprimir_recibo_remessa_antiga, name='cliente_imprimirReciboAntigo'),
]