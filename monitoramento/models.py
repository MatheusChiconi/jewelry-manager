from django.db import models
from django.conf import settings
from clientes.models import Cliente
from produtos.models import Produto
from decimal import Decimal

class Venda(models.Model):
    """
    Registra uma transação de venda completa.
    Este modelo centraliza as informações da venda, servindo como um "cabeçalho" da transação.
    """
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.SET_NULL, # Se o cliente for deletado, a venda não é perdida, apenas desvinculada.
        null=True,
        blank=True, # Permite vendas para clientes sem cadastro.
        related_name='vendas',
        verbose_name="Cliente"
    )
    responsavel = models.ForeignKey(
        settings.AUTH_USER_MODEL, # Link para o usuário do sistema (vendedor) que realizou a venda.
        on_delete=models.PROTECT, # Protege contra a exclusão de um usuário que tenha vendas registradas.
        related_name='vendas_realizadas',
        verbose_name="Responsável pela Venda"
    )

    # --- Dados da Venda ---
    FORMAS_PAGAMENTO = [
        ('PIX', 'Pix'),
        ('DEB', 'Cartão de Débito'),
        ('CRE', 'Cartão de Crédito'),
        ('DIN', 'Dinheiro'),
        ('OUT', 'Outro'),
    ]
    forma_pagamento = models.CharField(
        max_length=3,
        choices=FORMAS_PAGAMENTO,
        default='PIX',
        verbose_name="Forma de Pagamento",
    )
    data_venda = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data da Venda"
    )

    class Meta:
        verbose_name = "Venda"
        verbose_name_plural = "Vendas"
        ordering = ['-data_venda'] # As vendas mais recentes aparecerão primeiro no admin.

    def __str__(self):
        return f"Venda #{self.id} - {self.cliente.nome_completo if self.cliente else 'Sem Cadastro'}"
    
    def valor_total(self):
        """
        Calcula o valor total da venda somando todos os itens.
        Retorna: Decimal com o valor total da venda
        """
        total = Decimal('0.00')
        for item in self.itens.all():
            total += item.quantidade * item.preco_unitario_venda
        return total
    
    @property
    def total(self):
        """
        Property para acessar o valor total da venda de forma mais direta.
        Uso: venda.total
        """
        return self.valor_total()
    

class ItemVenda(models.Model):
    """
    Modelo de "junção" (through model) que detalha os produtos de cada venda.
    """
    venda = models.ForeignKey(
        Venda,
        on_delete=models.CASCADE,
        related_name='itens',
        verbose_name="Venda"
    )
    produto = models.ForeignKey(
        Produto,
        on_delete=models.PROTECT,
        related_name='itens_vendidos', 
        verbose_name="Produto"
    ) # Protege o produto de ser deletado se já foi vendido.
    quantidade = models.PositiveIntegerField(
        verbose_name="Quantidade"
    )
    preco_unitario_venda = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Preço Unitário na Venda" # Congela o preço no momento da venda.
    )

    class Meta:
        verbose_name = "Item da Venda"
        verbose_name_plural = "Itens da Venda"
        unique_together = ('venda', 'produto') # Garante que um produto não possa ser adicionado duas vezes na mesma venda.

    def __str__(self):
        return f"{self.quantidade}x {self.produto.nome} na Venda #{self.venda.id}"
