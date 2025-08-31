from django.contrib import admin
from .models import Venda, ItemVenda

# --- Versão Simplificada ---
# Esta é a forma mais básica de registrar seus modelos no painel de administração do Django.
# Cada modelo terá sua própria página de administração separada.

admin.site.register(Venda)
admin.site.register(ItemVenda)

