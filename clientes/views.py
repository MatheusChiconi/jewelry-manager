from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib import messages
from .forms import FornecedorForm
from .models import Cliente, Remessa
from django.db.models import Q
import json
from django.http import JsonResponse
from elderCadastro.gerarRecibo import gerar_recibo_pdf as gerar_recibo_pdf_func

# Create your views here.
def cliente_home(request):
    return render(request, 'clientes/cliente_home.html')

def cliente_cadastrarFornecedor(request):
    if request.method == 'POST':
        form = FornecedorForm(request.POST)
        if form.is_valid():
            fornecedor = form.save(commit=False)
        
            fornecedor.fornecedor = True
            
            fornecedor.save()
            
            messages.success(request, 'Fornecedor cadastrado com sucesso!')
            return redirect('cliente_cadastrarFornecedor') 
    else:
        form = FornecedorForm()
    return render(request, 'clientes/cliente_cadastrarFornecedor.html', {'form': form})

def cliente_cadastrarCliente(request):
    if request.method == 'POST':
        form = FornecedorForm(request.POST) # Use o seu formulário de cliente aqui
        if form.is_valid():
            form.save()
            messages.success(request, 'Cliente cadastrado com sucesso!')
            return redirect('cliente_cadastrarCliente') # Redireciona para a home ou lista de clientes
        else:
            messages.error(request, 'Por favor, corrija os erros no formulário.')
    else:
        form = FornecedorForm()

    return render(request, 'clientes/cliente_cadastrarCliente.html', {'form': form})

def cliente_selecionarCadastro(request):
    return render(request, 'clientes/cliente_selecionarCadastro.html')

def cliente_consultar(request):
    """
    View para listar e filtrar Clientes e Fornecedores.
    """
    # Começa com todos os registros, ordenados por nome.
    queryset = Cliente.objects.all().order_by('nome_completo')

    # Pega os valores dos filtros da URL (via GET)
    query_nome = request.GET.get('nome', '')
    query_doc = request.GET.get('cpf_cnpj', '')
    query_tel = request.GET.get('telefone', '')
    query_cidade = request.GET.get('cidade', '')
    query_tipo = request.GET.get('tipo', '')

    # Aplica os filtros se eles foram preenchidos
    if query_nome:
        queryset = queryset.filter(nome_completo__icontains=query_nome)
    
    if query_doc:
        queryset = queryset.filter(cpf_cnpj__icontains=query_doc)

    if query_tel:
        queryset = queryset.filter(telefone_whatsapp__icontains=query_tel)

    if query_cidade:
        # Supondo que a cidade está no campo 'endereco'
        queryset = queryset.filter(endereco__icontains=query_cidade)

    if query_tipo:
        if query_tipo == 'cliente':
            queryset = queryset.filter(fornecedor=False)
        elif query_tipo == 'fornecedor':
            queryset = queryset.filter(fornecedor=True)

    context = {
        'registros': queryset,
        # Envia os valores dos filtros de volta para preencher o formulário
        'valores_filtro': request.GET 
    }

    return render(request, 'clientes/cliente_consultar.html', context)

def cliente_historicoRemessa(request):
    """
    View para listar e filtrar o histórico de remessas de produtos para clientes.
    """
    
    # 1. Começamos com a consulta base, buscando todas as remessas.
    lista_remessas = Remessa.objects.select_related('cliente').order_by('-data_saida')

    # 2. Pegamos os valores dos filtros da URL.
    filtro_busca_cliente = request.GET.get('busca_cliente', '') # Novo campo de busca
    filtro_status = request.GET.get('status', '')

    # 3. Aplicamos os filtros na nossa consulta, se eles foram preenchidos.
    if filtro_busca_cliente:
        # Usamos um objeto Q para criar uma consulta OR (OU) nos campos do modelo Cliente relacionado.
        # Buscamos remessas cujo cliente tenha:
        # - O nome contendo o termo de busca, OU
        # - O CPF/CNPJ contendo o termo de busca, OU
        # - O telefone contendo o termo de busca, OU
        # - O ID da remessa contendo o termo de busca.
        lista_remessas = lista_remessas.filter(
            Q(cliente__nome_completo__icontains=filtro_busca_cliente) |
            Q(cliente__cpf_cnpj__icontains=filtro_busca_cliente) |
            Q(cliente__telefone_whatsapp__icontains=filtro_busca_cliente) |
            Q(id__icontains=filtro_busca_cliente)
        )

    # Filtro por Status (continua o mesmo)
    if filtro_status:
        lista_remessas = lista_remessas.filter(status=filtro_status)

    context = {
        'remessas': lista_remessas,
        'valores_filtro': request.GET,
    }

    return render(request, 'clientes/cliente_historicoRemessa.html', context)

def imprimir_recibo_remessa_antiga(request):
    """
    View para imprimir recibo de remessa antiga.
    """
    data = json.loads(request.body)
    remessaID = data.get('remessaID')
    remessa = Remessa.objects.get(id=remessaID)
    itensRemessa = remessa.itens.all()

    # Preparar dados para a função gerar_recibo_pdf_func
    nome_cliente = remessa.cliente.nome_completo
    data_saida = remessa.data_saida.strftime('%d/%m/%Y') if remessa.data_saida else 'N/A'
    tipoRemessa = 'EM ABERTO' if remessa.status == 'ABERTO' else 'FINALIZADO'

    count = 1
    my_prod = {}
    my_sale = {}
    codigo_barras = []

    for item in itensRemessa:
        item_quantidade = item.quantidade
        produto = item.produto
        produto_nome = produto.nome
        produto_codigo_barras = produto.codigo_barras
        preco_unitario = item.preco_venda_unitario_na_saida

        temp_list = [produto_nome, float(preco_unitario)]
        
        my_prod[count] = temp_list
        my_sale[count] = int(item_quantidade)
        codigo_barras.append(produto_codigo_barras)
        count += 1

    resultado = gerar_recibo_pdf_func(
                my_prod=my_prod,
                my_sale=my_sale,
                codigo_barras=codigo_barras,
                nome_cliente=nome_cliente,
                data_nota=data_saida,
                remessa_id=remessaID,
                situacao=tipoRemessa,
                retornar_bytes=True
            )
    
    return JsonResponse({
                'success': True,
                'pdf_base64': resultado['pdf_base64'],
                'nome_arquivo': resultado['nome_arquivo']
            })