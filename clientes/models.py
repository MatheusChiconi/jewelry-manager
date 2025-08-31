# -*- coding: utf-8 -*-

from django.db import models
from django.db.models import Sum, F
from django.utils import timezone
from decimal import Decimal

# É necessário importar o seu modelo de Produto para criar a relação
# Ajuste o caminho 'seu_app.models' se o modelo Produto estiver em outro lugar.
from produtos.models import Produto 

# Model 1: Cliente / Fornecedor (O "Quem")
# Centraliza as informações de contato. Um booleano diferencia clientes de fornecedores.
class Cliente(models.Model):
    # --- Campos de Identificação ---
    class TipoFornecedorChoices(models.TextChoices):
        FOLHEADO = 'FO', 'Folheado'
        OURO = 'OU', 'Ouro'
        PRATA = 'PR', 'Prata'
        OUTROS = 'OT', 'Outros'

    fornecedor = models.BooleanField(
        verbose_name='É Fornecedor?',
        default=False,
        help_text="Marque esta opção se o cadastro for de um fornecedor de produtos."
    )
    tipo_fornecedor = models.CharField(
        verbose_name="Produto Fornecido",
        max_length=2,
        choices=TipoFornecedorChoices.choices,
        default=TipoFornecedorChoices.FOLHEADO,
        help_text="Selecione o tipo do material que o fornecedor fornece.",
        blank=True,
        null=True
    )
    nome_completo = models.CharField(
        verbose_name='Nome Completo',
        max_length=200,
        help_text="Nome do cliente ou razão social do fornecedor."
    )
    cpf_cnpj = models.CharField(
        verbose_name='CPF/CNPJ',
        max_length=18,
        unique=True,
        blank=False, 
        null=False,
        help_text="Documento para identificação fiscal."
    )
    
    # --- Campos de Contato ---
    email = models.EmailField(
        verbose_name='E-mail',
        unique=True,
        blank=True, 
        null=True
    )
    telefone_whatsapp = models.CharField(
        verbose_name='Telefone / WhatsApp',
        max_length=15,
        blank=False,
        null=False
    )
    cep = models.CharField(
        verbose_name='CEP',
        max_length=10,
        blank=False,
        null=False,
        help_text="Informe o CEP."
    )
    cidade = models.CharField(
        verbose_name='Cidade',
        max_length=100,
        blank=False,
        null=False,
        help_text="Informe a cidade do cliente ou fornecedor."
    )
    estado = models.CharField(
        verbose_name='Estado',
        max_length=2,
        blank=False,
        null=False,
        help_text="Informe o estado (UF) do cliente ou fornecedor."
    )
    bairro = models.CharField(
        verbose_name='Bairro',
        max_length=100,
        blank=False,
        null=False,
        help_text="Informe o bairro do cliente ou fornecedor."
    )
    rua = models.CharField(
        verbose_name='Rua',
        max_length=200,
        blank=False,
        null=False,
        help_text="Informe a rua do cliente ou fornecedor."
    )
    numero = models.CharField(
        verbose_name='Número',
        max_length=10,
        blank=False,
        null=False,
        help_text="Informe o número do endereço (casa, apartamento, etc.)."
    )
    complemento = models.CharField(
        verbose_name='Complemento',
        max_length=100, 
        blank=True, 
        null=True,
        help_text="Informe o complemento do endereço (se houver)."
    )
    
    # --- Campos de Controle ---
    data_cadastro = models.DateTimeField(
        verbose_name='Data de Cadastro',
        auto_now_add=True,
        editable=False
    )

    class Meta:
        verbose_name = "Cliente ou Fornecedor"
        verbose_name_plural = "Clientes e Fornecedores"
        ordering = ['nome_completo']

    def __str__(self):
        if self.fornecedor:
            return f"{self.nome_completo} (Fornecedor de {self.get_tipo_fornecedor_display()})"
        else:
            return f"{self.nome_completo} (Cliente)"

    # --- Métodos de Negócio ---
    def get_saldo_devedor_total(self):
        """
        Calcula o valor total que o cliente deve, somando todos os itens marcados
        como 'Vendido' de todas as suas remessas que ainda estão 'Em Aberto'.
        """
        # Filtra todos os itens de remessa que pertencem a este cliente,
        # estão em uma remessa 'ABERTO' e foram marcados como 'VENDIDO'.
        total_vendido = ItemRemessa.objects.filter(
            remessa__cliente=self,
            remessa__status='ABERTO',
            status_item='VENDIDO'
        ).aggregate(
            # Multiplica a quantidade pelo preço unitário "congelado" de cada item.
            total=Sum(F('quantidade') * F('preco_venda_unitario_na_saida'), output_field=models.DecimalField())
        )['total']
        
        return total_vendido or Decimal('0.00')

# Model 2: Remessa (O "Quando e Qual Saída")
# Representa uma "sacola" de produtos que um cliente pegou em uma data específica.
class Remessa(models.Model):
    class StatusRemessa(models.TextChoices):
        EM_ABERTO = 'ABERTO', 'Em Aberto'
        FINALIZADO = 'FINALIZADO', 'Finalizado'

    # --- Relacionamentos e Datas ---
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.PROTECT, # Impede a exclusão de um cliente com remessas.
        related_name='remessas',
        verbose_name="Cliente"
    )
    data_saida = models.DateTimeField(
        verbose_name="Data da Saída",
        default=timezone.now
    )
    data_prevista_acerto = models.DateField(
        verbose_name="Data Prevista para Acerto",
        blank=True,
        null=True
    )
    data_acerto_final = models.DateTimeField(
        verbose_name="Data do Acerto Final",
        blank=True,
        null=True,
        editable=False
    )
    
    # --- Controle de Status ---
    status = models.CharField(
        max_length=10,
        choices=StatusRemessa.choices,
        default=StatusRemessa.FINALIZADO,
        verbose_name="Status da Remessa"
    )

    class Meta:
        verbose_name = "Remessa de Consignado"
        verbose_name_plural = "Remessas de Consignado"
        ordering = ['-data_saida']

    def __str__(self):
        return f"Remessa de {self.cliente.nome_completo} em {self.data_saida.strftime('%d/%m/%Y')}"

    # --- Métodos de Negócio ---
    def calcular_totais(self):
        """
        Calcula os totais de itens vendidos, devolvidos e ainda em posse do cliente
        para ESTA remessa específica.
        """
        itens = self.itens.all() # Usando o related_name 'itens' do ItemRemessa
        
        total_vendido = itens.filter(status_item='VENDIDO').aggregate(
            total=Sum(F('quantidade') * F('preco_venda_unitario_na_saida'))
        )['total'] or Decimal('0.00')
        
        total_devolvido = itens.filter(status_item='DEVOLVIDO').aggregate(
            total=Sum(F('quantidade') * F('preco_venda_unitario_na_saida'))
        )['total'] or Decimal('0.00')

        total_consignado = itens.filter(status_item='CONSIGNADO').aggregate(
            total=Sum(F('quantidade') * F('preco_venda_unitario_na_saida'))
        )['total'] or Decimal('0.00')

        return {
            'vendido': total_vendido,
            'devolvido': total_devolvido,
            'ainda_consignado': total_consignado,
        }
    
    def get_total_pecas(self):
        """
        Retorna o total de peças (itens) que estão nesta remessa.
        """
        return self.itens.aggregate(total=Sum('quantidade'))['total'] or 0
    
    def get_valor_total(self):
        """
        Retorna o valor total de todos os itens nesta remessa.
        """
        valor_total = self.itens.aggregate(
            total=Sum(F('quantidade') * F('preco_venda_unitario_na_saida'), output_field=models.DecimalField())
        )['total'] or Decimal('0.00')

        valor_total_string_formatted = f"R$ {valor_total:.2f}".replace('.', ',')
        return valor_total_string_formatted


# Model 3: ItemRemessa (O "O Quê e Quanto")
# Detalha cada produto dentro de uma remessa, com sua quantidade e status.
class ItemRemessa(models.Model):
    class StatusItem(models.TextChoices):
        CONSIGNADO = 'CONSIGNADO', 'Consignado'
        VENDIDO = 'VENDIDO', 'Vendido'
        DEVOLVIDO = 'DEVOLVIDO', 'Devolvido'

    # --- Relacionamentos e Dados do Item ---
    remessa = models.ForeignKey(
        Remessa,
        on_delete=models.CASCADE, # Se a remessa for deletada, os itens vão junto.
        related_name='itens',
        verbose_name="Remessa"
    )
    produto = models.ForeignKey(
        Produto,
        on_delete=models.PROTECT, # Impede a exclusão de um produto em uma remessa.
        verbose_name="Produto"
    )
    quantidade = models.PositiveIntegerField(
        verbose_name="Quantidade"
    )
    # "Congela" o preço do produto no momento da saída, garantindo consistência histórica.
    preco_venda_unitario_na_saida = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Preço Unitário na Saída"
    )
    status_item = models.CharField(
        max_length=12,
        choices=StatusItem.choices,
        default=StatusItem.CONSIGNADO,
        verbose_name="Status do Item"
    )

    class Meta:
        verbose_name = "Item da Remessa"
        verbose_name_plural = "Itens da Remessa"
        unique_together = ('remessa', 'produto') # Garante que não haja o mesmo produto duas vezes na mesma remessa.

    def __str__(self):
        return f"{self.quantidade}x {self.produto.nome} ({self.status_item})"
    
    def save(self, *args, **kwargs):
        # Se o item está sendo criado pela primeira vez...
        if self.pk is None:
            # 1. "Congela" o preço de venda do produto no momento da criação.
            self.preco_venda_unitario_na_saida = self.produto.preco_venda
            
            # 2. Subtrai a quantidade do estoque principal do produto.
            if self.produto.estoque >= self.quantidade:
                self.produto.estoque = F('estoque') - self.quantidade
                self.produto.save(update_fields=['estoque'])
            else:
                raise ValueError(f"Estoque insuficiente para o produto {self.produto.nome}.")

        super().save(*args, **kwargs)

    # --- Métodos de Negócio ---
    def devolver_ao_estoque(self, quantidade_devolver):
        """
        Muda o status do item para 'Devolvido' e retorna a quantidade
        correspondente de volta ao estoque principal do produto.
        Só permite devolver até a quantidade consignada.
        """
        if self.status_item == 'CONSIGNADO' and 0 < quantidade_devolver <= self.quantidade:
            self.quantidade -= quantidade_devolver
            self.produto.estoque = F('estoque') + quantidade_devolver
            self.produto.save(update_fields=['estoque'])
            # Se toda a quantidade foi devolvida, muda o status para DEVOLVIDO
            if self.quantidade == 0:
                self.status_item = 'DEVOLVIDO'
            self.save(update_fields=['quantidade', 'status_item'])
            return True
        return False  # Retorna False se a ação não pôde ser executada.
