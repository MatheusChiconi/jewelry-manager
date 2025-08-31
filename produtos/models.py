from decimal import Decimal
import io
import json

import barcode
from barcode.ean import EuropeanArticleNumber13
from barcode.writer import SVGWriter
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q, Sum
from django.http import HttpResponse
from reportlab.graphics import renderPDF
from reportlab.lib.units import inch, mm
from reportlab.pdfgen import canvas
from svglib.svglib import svg2rlg


class TipoPeca(models.Model):
    nome = models.CharField(
        verbose_name="Tipo de Peça",
        max_length=100,
        unique=True,
        help_text="Nome do tipo de peça, como 'Anel', 'Brinco', etc."
    )
    def __str__(self):
        return self.nome
    
class CustomEAN13(EuropeanArticleNumber13):
    def __init__(self, code, writer=None):
        self._validate(code)
        self.code = code
        self.writer = writer or SVGWriter()

class Produto(models.Model):

    class TipoProduto(models.TextChoices):
        FOLHEADO = 'FO', 'Folheado'
        OURO = 'OU', 'Ouro'
        PRATA = 'PR', 'Prata'

    nome = models.CharField(
        verbose_name="Nome do Produto",
        max_length=200, 
        unique=True,
        help_text="Nome principal do produto, como aparecerá na nota e nas etiquetas."
    )
    tipo = models.CharField(
        verbose_name="Tipo do Produto",
        max_length=2,
        choices=TipoProduto.choices,
        default=TipoProduto.FOLHEADO,
        help_text="Selecione o tipo do material do produto."
    )
    tipo_peca = models.ForeignKey(
        TipoPeca,
        verbose_name="Tipo de Peça",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        help_text="Selecione o tipo de peça, como 'Anel', 'Brinco', etc."
    )
    fornecedor = models.ForeignKey(
        'clientes.Cliente',
        verbose_name="Fornecedor",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        help_text="Selecione o fornecedor deste produto, se aplicável.",
        limit_choices_to=Q(fornecedor=True)  # Apenas fornecedores
    )
    estoque = models.PositiveIntegerField(
        verbose_name="Quantidade em Estoque",
        default=0,
        help_text="A quantidade atual de unidades deste produto disponíveis para venda."
    )
    gramas = models.DecimalField(
        verbose_name="Peso (gramas)",
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text="Informe o peso do produto em gramas (se for ouro).",
        blank=True,
        null=True
    )
    custo = models.DecimalField(
        verbose_name="Preço de Custo (R$)",
        max_digits=10, 
        decimal_places=2,
        help_text="O valor que você pagou pelo produto.",
        blank=True,
        null=True,
    )
    margem_lucro = models.DecimalField(
        verbose_name="Margem de Lucro (%)",
        max_digits=5,
        decimal_places=2,
        default=100.00
    )
    preco_venda = models.DecimalField(
        verbose_name="Preço Final de Venda (R$)",
        max_digits=10, 
        decimal_places=2,
        blank=True,
        null=True,
        editable=False
    )
    codigo_barras = models.CharField(
        verbose_name="Código de Barras",
        max_length=13,
        unique=True,
        blank=True,
        null=True,
        help_text="Digite um código de até 13 números ou deixe em branco para gerar um código interno."
    )

    def __str__(self):
        return self.nome

    @classmethod
    def imprimir_etiquetas(cls, request):
        """
        Método de classe que gera um arquivo PDF com etiquetas para os produtos
        solicitados na requisição.
        """
        if request.method != 'POST':
            return HttpResponse(status=405)

        try:
            data = json.loads(request.body)
            produtos_solicitados = data.get('produtos', [])
            
            buffer_pdf = io.BytesIO()
            largura_pagina = 2.3 * inch
            altura_pagina = 0.47 * inch
            c = canvas.Canvas(buffer_pdf, pagesize=(largura_pagina, altura_pagina))

            for produto_info in produtos_solicitados:
                id_produto = produto_info.get('id')
                quantidade = int(produto_info.get('quantidade', 1))

                try:
                    produto_bd = cls.objects.get(id=id_produto)
                    nome_produto = produto_bd.nome
                    codigo_barras = produto_bd.codigo_barras
                    
                    if produto_bd.preco_venda is not None and produto_bd.preco_venda > 0:
                        valor_base = produto_bd.preco_venda
                    else:
                        valor_base = produto_bd.gramas

                except cls.DoesNotExist:
                    nome_produto = 'Produto Desconhecido'
                    codigo_barras = '0000000000000'
                    valor_base = None

                for _ in range(quantidade):
                    # NOVA FORMATAÇÃO DO NOME DO PRODUTO
                    nome_cortado = nome_produto[:48]
                    primeira_linha = nome_cortado[:16]
                    segunda_linha = nome_cortado[16:32]
                    terceira_linha = nome_cortado[32:48]

                    # Ignora espaço inicial de cada linha
                    if primeira_linha and primeira_linha[0] == " ":
                        primeira_linha = primeira_linha[1:]
                    if segunda_linha and segunda_linha[0] == " ":
                        segunda_linha = segunda_linha[1:]
                    if terceira_linha and terceira_linha[0] == " ":
                        terceira_linha = terceira_linha[1:]

                    # Reduzir tamanho da fonte para 1/3 do original (mínimo 6)
                    tamanho_fonte_produto = max(6, 11 // 3)

                    EAN = barcode.get_barcode_class('ean13')
                    ean_barcode = EAN(codigo_barras, writer=SVGWriter())
                    writer_options = {
                        'module_width': 0.25, 'module_height': 7.5,
                        'font_size': 5.5, 'text_distance': 2,
                    }
                    buffer_svg = io.BytesIO()
                    ean_barcode.write(buffer_svg, options=writer_options)
                    buffer_svg.seek(0)

                    desenho_barcode = svg2rlg(buffer_svg)
                    largura_real_barcode = desenho_barcode.width
                    altura_real_barcode = desenho_barcode.height
                    largura_estimada_texto = 18 * (tamanho_fonte_produto * 0.4)
                    largura_total_conteudo = largura_real_barcode + (2 * mm) + largura_estimada_texto

                    x_inicial = (largura_pagina - largura_total_conteudo) / 2 + 6
                    y_inicial = (altura_pagina - altura_real_barcode) / 2 - 2

                    renderPDF.draw(desenho_barcode, c, x_inicial, y_inicial)

                    posicao_x_texto = x_inicial + largura_real_barcode - (2 * mm) - 0
                    posicao_y_texto = 8 + y_inicial + (altura_real_barcode / 2) - (tamanho_fonte_produto / 2) + 3
                    c.setFont("Helvetica", tamanho_fonte_produto)
                    c.drawString(posicao_x_texto, posicao_y_texto, primeira_linha)
                    if segunda_linha:
                        c.drawString(posicao_x_texto, posicao_y_texto - (tamanho_fonte_produto - 1), segunda_linha)
                    if terceira_linha:
                        c.drawString(posicao_x_texto, posicao_y_texto - 2 * (tamanho_fonte_produto - 1), terceira_linha)

                    if valor_base is not None:
                        valor_em_centavos = int(Decimal(valor_base) * 100)
                        valor_formatado_str = f"{valor_em_centavos:04d}"
                        valor_oculto_str = f"0300{valor_formatado_str}"
                        posicao_y_inferior = posicao_y_texto - 15  # <-- posição Y dos números embaixo do nome do produto
                        c.drawString(posicao_x_texto, posicao_y_inferior, valor_oculto_str)

                    c.showPage()

            c.save()
            pdf_content = buffer_pdf.getvalue()
            buffer_pdf.close()

            response = HttpResponse(pdf_content, content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename=\"etiquetas.pdf\"'
            
            return response

        except Exception as e:
            return HttpResponse(f"Erro ao gerar PDF de etiquetas: {str(e)}", status=400)

    @classmethod
    def get_valor_total_estoque(cls):
        """
        Calcula e retorna a soma do 'preco_venda' de todos os produtos
        multiplicado pela sua quantidade em estoque (ex: 12.345,67).
        """
        valor_total = cls.objects.aggregate(
            total=Sum(models.F('preco_venda') * models.F('estoque'))
        )['total'] or Decimal('0.00')

        valor_formatado = f"{valor_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        
        return valor_formatado
    
    @classmethod
    def get_quantidade_total_estoque(cls):
        """
        Calcula e retorna a soma de todas as quantidades em estoque
        de todos os produtos, formatado como string.
        """
        quantidade_total = cls.objects.aggregate(
            total=Sum('estoque')
        )['total'] or 0
        return str(quantidade_total)
    
    def _gerar_codigo_interno(self) -> str:
        """
        Gera um código de barras interno de 13 dígitos com base no tipo do produto.
        - Folheado (0): 0 PPPPP VVVVVV V
        - Prata (1):    1 PPPPP VVVVVV V
        - Ouro (2):     2 PPPPP GGGGGG V
        (PPPPP: número do produto com 5 dígitos, V: dígito verificador EAN13)
        """
        if self.pk is None or self.pk > 99999:
            raise ValidationError(
                {'codigo_barras': 'Geração automática não suportada para IDs > 99999.'}
            )
        
        identificador_produto = f"{self.pk:05d}"
        
        if self.tipo == self.TipoProduto.OURO:
            # Lógica para Ouro
            prefixo = "2"
            
            if self.gramas is None or self.gramas <= 0 or self.gramas >= 10000:
                raise ValidationError(
                    {'codigo_barras': 'Para Ouro, o peso deve ser informado (maior que 0 e menor que 10.000g) para geração automática.'}
                )
            
            gramas_em_centigramas = int(self.gramas * 100)
            conteudo_codificado = f"{gramas_em_centigramas:06d}"

        else:
            prefixo = "0" if self.tipo == self.TipoProduto.FOLHEADO else "1"

            if self.preco_venda is None or self.preco_venda >= 1000000:
                raise ValidationError(
                    {'codigo_barras': 'Geração automática não suportada para preços >= R$ 1.000.000,00.'}
                )
            preco_inteiro = int(self.preco_venda)
            conteudo_codificado = f"{preco_inteiro:06d}"

        base_code = f"{prefixo}{identificador_produto}{conteudo_codificado}"
        
        # Calcula o dígito verificador EAN13
        soma = 0
        for i, digito in enumerate(base_code):
            if i % 2 == 0:
                soma += int(digito)
            else:
                soma += int(digito) * 3
        
        digito_verificador = (10 - (soma % 10)) % 10
        
        return f"{base_code}{digito_verificador}"

    def save(self, *args, **kwargs):
        if self.tipo != self.TipoProduto.OURO:
            if self.custo is not None and self.margem_lucro is not None:
                fator = Decimal('1') + (self.margem_lucro / Decimal('100'))
                preco_calculado = self.custo * fator
                self.preco_venda = preco_calculado.quantize(Decimal('0.01'))
            else:
                self.preco_venda = Decimal('0.00')
        else:
            if self.preco_venda is None:
                self.preco_venda = Decimal('0.00')

        is_new = self.pk is None
        codigo_barras_esta_vazio = not self.codigo_barras

        super().save(*args, **kwargs)

        if is_new and codigo_barras_esta_vazio:
            try:
                self.codigo_barras = self._gerar_codigo_interno()
                super().save(update_fields=['codigo_barras'])
            except ValidationError as e:
                raise e
