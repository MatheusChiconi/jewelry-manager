from django import forms
from .models import Cliente

class FornecedorForm(forms.ModelForm):
    class Meta:
        model = Cliente
        
        # MUDANÇA AQUI: Adicionamos 'tipo_fornecedor' à lista de campos.
        fields = ['tipo_fornecedor', 'nome_completo', 'cpf_cnpj', 'email', 'telefone_whatsapp', 'cep', 'cidade', 'bairro', 'rua', 'numero', 'complemento']

        widgets = {
            # Adicionamos o widget para o novo campo
            'tipo_fornecedor': forms.Select(attrs={'class': 'form-select'}),
            'nome_completo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Digite o nome do fornecedor'
            }),
            'cpf_cnpj': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Apenas números'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'email@fornecedor.com'
            }),
            'telefone_whatsapp': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '(XX) XXXXX-XXXX'
            }),
            'cep': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'XXXXX-XXX'
            }),
            'cidade': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Cidade'
            }),
            'bairro': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Bairro'
            }),
            'rua': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Rua'
            }),
            'numero': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número'
            }),
            'complemento': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Complemento (opcional)'
            }),
        }
