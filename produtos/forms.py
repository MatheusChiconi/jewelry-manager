from django import forms
from .models import Produto

class ProdutoFolheadoPrataForm(forms.ModelForm):
    class Meta:
        model = Produto
        
        fields = ['nome', 'estoque', 'custo', 'margem_lucro', 'codigo_barras', 'tipo_peca', 'fornecedor']

        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Colar Coração Zircônia'
            }),
            'estoque': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
            }),
            'custo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: 25,50'
            }),
            'margem_lucro': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'codigo_barras': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'tipo_peca': forms.Select(attrs={
                'class': 'form-control',
            }),
            'fornecedor': forms.Select(attrs={
                'class': 'form-control',
            }),
        }

        labels = {
            'nome': 'Nome do Produto',
            'estoque': 'Quantidade em Estoque',
            'custo': 'Preço de Custo (R$)',
            'margem_lucro': 'Margem de Lucro (%)',
            'codigo_barras': 'Código de Barras',
            'tipo_peca': 'Tipo de Peça',
            'fornecedor': 'Fornecedor',
        }

class ProdutoOuroForm(forms.ModelForm):
    class Meta:
        model = Produto
        
        fields = ['nome', 'estoque', 'gramas', 'codigo_barras', 'tipo_peca', 'fornecedor']

        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Anel Solitário Ouro 18k'
            }),
            'estoque': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
            }),
            'gramas': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: 4,50'
            }),
            'codigo_barras': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'tipo_peca': forms.Select(attrs={
                'class': 'form-control',
            }),
            'fornecedor': forms.Select(attrs={
                'class': 'form-control',
            }),
        }

        labels = {
            'nome': 'Nome do Produto',
            'estoque': 'Quantidade em Estoque',
            'gramas': 'Peso (gramas)',
            'codigo_barras': 'Código de Barras',
            'tipo_peca': 'Tipo de Peça',
            'fornecedor': 'Fornecedor',
        }