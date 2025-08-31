"""
URL configuration for elderCadastro project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from elderCadastro import views
from django.urls import include
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('acesso-negado/', views.acesso_negado, name='acesso_negado'),
    path('logout/', LogoutView.as_view(), name='logout'),

    path('produtos/', include('produtos.urls')),
    path('clientes/', include('clientes.urls')),

    path('registrar_saida/', views.registrar_saida, name='registrar_saida'),
    path('buscar_clientes_api/', views.buscar_clientes_api, name='buscar_clientes_api'),
    path('buscar_produto_api/', views.buscar_produto_api, name='buscar_produto_api'),
    path('salvar_remessa_api/', views.salvar_remessa_api, name='salvar_remessa_api'),
    path('gerar_recibo_pdf/', views.gerar_recibo_pdf_view, name='gerar_recibo_pdf'),

    path('acerto_contas/', views.pagina_acerto_contas, name='acerto_contas'),
    path('buscar_remessas_api/', views.buscar_remessas_api, name='buscar_remessas_api'),
    path('detalhes_remessa_api/<int:remessa_id>/', views.detalhes_remessa_api, name='detalhes_remessa_api'),
    path('finalizar_acerto_api/', views.finalizar_acerto_api, name='finalizar_acerto_api'),
]
