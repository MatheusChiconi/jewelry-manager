from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.db import transaction
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_GET
from django.contrib import messages
from decimal import Decimal
import json
import io
from reportlab.lib.pagesizes import inch, mm
from reportlab.pdfgen import canvas
from reportlab.graphics import renderPDF
from svglib.svglib import svg2rlg
import barcode
from barcode.writer import SVGWriter

from .forms import ProdutoFolheadoPrataForm, ProdutoOuroForm
from .models import Produto

# Create your views here.
def produto_home(request):
    return render(request, 'produtos/produto_home.html')

def produto_tipo(request):
    return render(request, 'produtos/produto_tipo.html')

def produto_cadastrar_folheado(request):
    if request.method == 'POST':
        form = ProdutoFolheadoPrataForm(request.POST)

        if form.is_valid():
            produto = form.save(commit=False)
            
            produto.tipo = Produto.TipoProduto.FOLHEADO
            produto.save()
            
            messages.success(request, 'Produto cadastrado com sucesso!')
            return redirect('produto_cadastrar_folheado')
        else:
            messages.error(request, 'Por favor, corrija os erros no formulário.')
    
    else:
        form = ProdutoFolheadoPrataForm()
    return render(request, 'produtos/produto_cadastrar_folheado.html/', {'form': form})

def produto_cadastrar_prata(request):
    if request.method == 'POST':
        form = ProdutoFolheadoPrataForm(request.POST)

        if form.is_valid():
            produto = form.save(commit=False)
            
            produto.tipo = Produto.TipoProduto.PRATA
            produto.save()
            messages.success(request, 'Produto cadastrado com sucesso!')
            return redirect('produto_cadastrar_prata')
        else:
            messages.error(request, 'Por favor, corrija os erros no formulário.')
    
    else:
        form = ProdutoFolheadoPrataForm()
    return render(request, 'produtos/produto_cadastrar_prata.html', {'form': form})

def produto_cadastrar_ouro(request):
    if request.method == 'POST':
        form = ProdutoOuroForm(request.POST)

        if form.is_valid():
            produto = form.save(commit=False)

            if produto.gramas <= Decimal('0.00'):
                messages.error(request, 'A quantidade de gramas deve ser maior que zero.')
                return render(request, 'produtos/produto_cadastrar_ouro.html', {'form': form})
            
            produto.tipo = Produto.TipoProduto.OURO
            produto.save()

            messages.success(request, 'Produto cadastrado com sucesso!')
            return redirect('produto_cadastrar_ouro')
        
        else:
            messages.error(request, 'Por favor, corrija os erros no formulário.')
    
    else:
        form = ProdutoOuroForm()
    return render(request, 'produtos/produto_cadastrar_ouro.html', {'form': form})

def produto_consultar(request):
    lista_produtos = Produto.objects.all().order_by('-id')

    termo_busca = request.GET.get('buscar')
    filtro_tipo = request.GET.get('tipo')
    if termo_busca:
        lista_produtos = lista_produtos.filter(
            Q(nome__icontains=termo_busca) | 
            Q(codigo_barras__icontains=termo_busca)
        )

    if filtro_tipo:
        lista_produtos = lista_produtos.filter(tipo=filtro_tipo)

    context = {
        'produtos': lista_produtos,
        'termo_busca_valor': termo_busca or "",
        'filtro_tipo_valor': filtro_tipo or "",
    }
    return render(request, 'produtos/produto_consultar.html/', context)

@login_required
@require_POST
def deletar_produto(request, produto_id):
    produto = get_object_or_404(Produto, pk=produto_id)
    
    try:
        nome_produto = produto.nome
        produto.delete()
        messages.success(request, f'O produto "{nome_produto}" foi excluído com sucesso.')
        
    except Exception as e:
        messages.error(request, f'Ocorreu um erro ao tentar excluir o produto: {e}')
    return redirect('produto_consultar')

@login_required
def pagina_edicao_estoque(request):
    # Exibe a página de edição de estoque.
    return render(request, 'produtos/produto_editar_estoque.html')

@login_required
@require_GET
def buscar_produto_api(request):
    # Retorna os dados de um produto pelo código de barras em formato JSON.
    codigo = request.GET.get('codigo', None)
    if not codigo:
        return JsonResponse({'status': 'error', 'message': 'Nenhum código de barras fornecido.'}, status=400)
    try:
        produto = Produto.objects.get(codigo_barras=codigo)
        dados_produto = {
            'id': produto.id,
            'nome': produto.nome,
            'estoque_atual': produto.estoque,
        }
        return JsonResponse({'status': 'success', 'produto': dados_produto})
    except Produto.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Produto não encontrado.'}, status=404)

@login_required
@require_POST
def salvar_estoque_api(request):
    # Atualiza o estoque de uma lista de produtos recebida via JSON.
    try:
        data = json.loads(request.body)
        produtos_para_atualizar = data.get('produtos', [])
        if not isinstance(produtos_para_atualizar, list):
            raise ValueError("Os dados enviados não estão no formato de lista esperado.")
        with transaction.atomic():
            for item in produtos_para_atualizar:
                produto_id = item.get('id')
                nova_quantidade = int(item.get('nova_quantidade'))
                if nova_quantidade < 0:
                    raise ValueError(f"A quantidade de estoque para o produto ID {produto_id} não pode ser negativa.")
                Produto.objects.filter(pk=produto_id).update(estoque=nova_quantidade)
        return JsonResponse({'status': 'success', 'message': 'Estoque atualizado com sucesso!'})
    except (json.JSONDecodeError, ValueError, KeyError) as e:
        return JsonResponse({'status': 'error', 'message': f'Erro nos dados enviados: {e}'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Ocorreu um erro inesperado: {e}'}, status=500)

def gerar_etiqueta(request):
    context = {
        'produtos': Produto.objects.all(),
    }
    return render(request, 'produtos/produto_gerar_etiqueta.html', context)


def imprimir_etiquetas(request):
    """
    View que delega a geração do PDF de etiquetas para o método
    correspondente no modelo Produto.
    """
    # A view apenas chama o método de classe e retorna o que ele produzir.
    return Produto.imprimir_etiquetas(request)