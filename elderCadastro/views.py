from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from produtos.models import Produto
from clientes.models import Cliente, Remessa, ItemRemessa
from monitoramento.models import Venda, ItemVenda
from django.http import JsonResponse
from django.db import transaction
from django.db.models import Q
from django.views.decorators.http import require_GET, require_POST
import json
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from .gerarRecibo import indexar_acerto, gerar_recibo_pdf as gerar_recibo_pdf_func

def total_geral_pecas_consignado():
    """
    Retorna o total geral de peças consignadas.
    """
    valor = 0
    
    pecas = ItemRemessa.objects.filter(status_item='CONSIGNADO')
    for peca in pecas:
        valor += peca.quantidade
    return valor

def total_geral_valor_consignadas():
    """
    Retorna o valor total de peças consignadas.
    """
    valor = 0

    itens_consignados = ItemRemessa.objects.filter(status_item='CONSIGNADO')
    for item in itens_consignados:
        valor += item.preco_venda_unitario_na_saida * item.quantidade

    valor_formatado = f"R$ {valor:.2f}".replace('.', ',')
    return valor_formatado


@login_required
def home(request):

    valor_estoque = Produto.get_valor_total_estoque()
    quantidade_estoque = Produto.get_quantidade_total_estoque()
    total_pecas_consignadas = total_geral_pecas_consignado()
    total_valor_consignadas = total_geral_valor_consignadas()

    context = {
        'valor_estoque': valor_estoque,
        'quantidade_estoque': quantidade_estoque,
        'total_pecas_consignadas': total_pecas_consignadas,
        'total_valor_consignadas': total_valor_consignadas,
    }

    return render(request, 'home.html', context)

def acesso_negado(request):
    return render(request, 'negado.html')

# --- A PARTIR DAQUI É SOBRE A PÁGINA DE SAÍDA ---
@login_required
def registrar_saida(request):
    """
    Renderiza a página principal para registro de saídas (venda ou consignado).
    """
    return render(request, 'registrar_saida.html')

# --- API para buscar clientes ---
@login_required
@require_GET
def buscar_clientes_api(request):
    """
    API para a busca dinâmica de clientes no modal.
    """
    termo_busca = request.GET.get('q', '')
    clientes = Cliente.objects.filter(fornecedor=False)

    if termo_busca:
        clientes = clientes.filter(
            Q(nome_completo__icontains=termo_busca) |
            Q(cpf_cnpj__icontains=termo_busca) |
            Q(telefone_whatsapp__icontains=termo_busca)
        )
    
    clientes = clientes[:10] 
    
    dados_clientes = [
        {'id': cliente.id, 'nome': cliente.nome_completo, 'doc': cliente.cpf_cnpj or ''}
        for cliente in clientes
    ]
    return JsonResponse({'clientes': dados_clientes})


# --- API para salvar a remessa ---
@login_required
@require_POST
def salvar_remessa_api(request):
    """
    API para receber os dados da nova remessa e salvá-la no banco de dados.
    """
    try:
        data = json.loads(request.body)
        cliente_id = data.get('cliente_id')
        tipo_remessa = data.get('tipo_remessa')  # 'VENDA' ou 'CONSIGNADO'
        produtos = data.get('produtos', [])

        if not all([cliente_id, tipo_remessa, produtos]):
            return JsonResponse({'status': 'error', 'message': 'Dados incompletos.'}, status=400)

        with transaction.atomic():
            cliente = Cliente.objects.get(pk=cliente_id)

            # Cria a remessa principal
            nova_remessa = Remessa.objects.create(
                cliente=cliente,
                status='FINALIZADO' if tipo_remessa == 'VENDA' else 'ABERTO'
            )
            
            # Se for uma venda salva no histórico de vendas
            if tipo_remessa == 'VENDA':
                formaPagamento = data.get('forma_pagamento')
                
                #debug
                print(formaPagamento)

                nova_venda = Venda.objects.create(
                    cliente=cliente,
                    responsavel=request.user,
                    forma_pagamento=formaPagamento,
                )

            for item_data in produtos:
                produto_id = item_data['id']
                quantidade = int(item_data['quantidade'])

                produto = Produto.objects.get(pk=produto_id)

                if produto.estoque < quantidade:
                    raise ValueError(f"Estoque insuficiente para o produto: {produto.nome}")

                ItemRemessa.objects.create(
                    remessa=nova_remessa,
                    produto=produto,
                    quantidade=quantidade,
                    preco_venda_unitario_na_saida=produto.preco_venda,
                    status_item='VENDIDO' if tipo_remessa == 'VENDA' else 'CONSIGNADO'
                )

                if tipo_remessa == 'VENDA':
                    # Cria o item de venda para monitoramento
                    ItemVenda.objects.create(
                        venda=nova_venda,
                        produto=produto,
                        quantidade=quantidade,
                        preco_unitario_venda=produto.preco_venda
                    )

        return JsonResponse({'status': 'success', 'message': 'Remessa registrada com sucesso!', 'id': nova_remessa.id})

    except Cliente.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Cliente não encontrado.'}, status=404)

    except Produto.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Um dos produtos não foi encontrado.'}, status=404)

    except ValueError as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Ocorreu um erro inesperado: {e}'}, status=500)

@login_required
@require_GET
def buscar_produto_api(request):
    """
    API que o JavaScript usa para encontrar um produto pelo seu código de barras.
    """
    codigo = request.GET.get('codigo', None)

    if not codigo:
        return JsonResponse({'status': 'error', 'message': 'Nenhum código de barras fornecido.'}, status=400)

    try:
        produto = Produto.objects.get(codigo_barras=codigo)
        
        dados_produto = {
            'id': produto.id,
            'nome': produto.nome,
            'preco_venda': produto.preco_venda,
            'estoque_atual': produto.estoque,
        }
        
        return JsonResponse({'status': 'success', 'produto': dados_produto})

    except Produto.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Produto com este código não encontrado.'}, status=404)
# - AQUI TERMINA A PÁGINA DE SAÍDA -


# - AQUI COMEÇA A PÁGINA DE ACERTO DE CONTAS -
@login_required
def pagina_acerto_contas(request):
    """
    Renderiza a página principal para o acerto de contas.
    """
    return render(request, 'acerto_contas.html')

@login_required
@require_GET
def buscar_remessas_api(request):
    """
    API para buscar remessas com status 'ABERTO' para o modal de seleção.
    """
    termo_busca = request.GET.get('q', '')
    remessas = Remessa.objects.filter(status='ABERTO').select_related('cliente')

    if termo_busca:
        remessas = remessas.filter(
            Q(cliente__nome_completo__icontains=termo_busca) |
            Q(cliente__cpf_cnpj__icontains=termo_busca)
        )
    
    remessas = remessas.order_by('-data_saida')[:10]
    
    dados_remessas = [{
        'id': r.id,
        'cliente_nome': r.cliente.nome_completo,
        'data_saida': r.data_saida.strftime('%d/%m/%Y')
    } for r in remessas]
    
    return JsonResponse({'remessas': dados_remessas})

@login_required
@require_GET
def detalhes_remessa_api(request, remessa_id):
    """
    API que retorna todos os itens de uma remessa específica.
    """
    try:
        remessa = Remessa.objects.get(pk=remessa_id, status='ABERTO')
        data_saida = remessa.data_saida.strftime('%d/%m/%Y') if remessa.data_saida else 'N/A'
        cliente = remessa.cliente
        nome_cliente = cliente.nome_completo if cliente else 'Cliente Desconhecido'
        itens = ItemRemessa.objects.filter(remessa=remessa, status_item='CONSIGNADO').select_related('produto')

        dados_itens = [{
            'id': item.id,
            'produto_id': item.produto.id,
            'produto_nome': item.produto.nome,
            'codigo_barras': item.produto.codigo_barras,
            'quantidade': item.quantidade,
            'preco_unitario': item.preco_venda_unitario_na_saida
        } for item in itens]

        dados_remessa = {
            'cliente_nome': nome_cliente,
            'data_saida': data_saida,
            'itens': dados_itens
        }

        return JsonResponse({'status': 'success', 'dados': dados_remessa})
    except Remessa.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Remessa não encontrada ou já finalizada.'}, status=404)

@login_required
@require_POST
def finalizar_acerto_api(request):
    """
    API para processar o acerto de contas.
    Recebe os itens devolvidos e a ação final (manter aberto ou fechar).
    """
    try:
        data = json.loads(request.body)
        itens = data.get('itens', [])
        acao_final = data.get('acao_final')
        remessa_id = data.get('remessa_id')
        if acao_final == 'FECHAR':
            formaPagamento = data.get('forma_pagamento')

        with transaction.atomic():
            remessa = Remessa.objects.get(pk=remessa_id)

            if acao_final == 'FECHAR':
                venda_nova = Venda.objects.create(
                    cliente=remessa.cliente,
                    responsavel=request.user,
                    forma_pagamento=formaPagamento
                )

            # Buscar todos os itens CONSIGNADOS que estão atualmente na remessa
            itens_atuais_na_remessa = ItemRemessa.objects.filter(
                remessa=remessa, 
                status_item='CONSIGNADO'
            ).select_related('produto')
            
            # Criar um conjunto com os IDs dos itens que vieram do frontend
            ids_itens_recebidos = {item_['id'] for item_ in itens}
            
            # Preparar lista de itens que continuam e identificar produtos removidos
            itens_continuam = []
            produtos_removidos = {}
            
            for item_ in itens:
                item_id = item_['id']
                item = ItemRemessa.objects.get(pk=item_id, remessa=remessa)
                quantidade_antes = item.quantidade
                quantidade_depois = item_['quantidade']
                quantidade_a_ser_devolvida = quantidade_antes - quantidade_depois
                
                print(f"Produto: {item.produto.nome} Quantidade antes: {quantidade_antes}, Quantidade depois: {quantidade_depois}, Devolvida: {quantidade_a_ser_devolvida}")
                
                # Se a quantidade depois é 0, o produto foi completamente removido
                if quantidade_depois == 0:
                    produtos_removidos[item.produto.nome] = quantidade_antes
                # Se a quantidade depois > 0, o produto continua (parcialmente)
                elif quantidade_depois > 0:
                    itens_continuam.append({
                        'nome': item.produto.nome,
                        'quantidade': quantidade_depois,
                        'preco_unitario': float(item.preco_venda_unitario_na_saida)
                    })
                
                if acao_final == 'FECHAR':
                    # Cadastrar os itens que ficaram na remessa no ItemVenda
                    if quantidade_depois > 0:
                        ItemVenda.objects.create(
                            venda=venda_nova,
                            produto=item.produto,
                            quantidade=quantidade_depois,
                            preco_unitario_venda=item.preco_venda_unitario_na_saida
                        )

                # Devolver ao estoque a quantidade calculada
                item.devolver_ao_estoque(quantidade_a_ser_devolvida)
                item.save()
            
            # Log dos produtos removidos para debug
            if produtos_removidos:
                print(f"Produtos REALMENTE removidos da remessa: {produtos_removidos}")
            else:
                print("Nenhum produto foi completamente removido da remessa")

            if acao_final == 'FECHAR':
                remessa.status = 'FINALIZADO'
                remessa.save()
            else:
                remessa.status = 'ABERTO'
                remessa.data_saida = timezone.now()
                remessa.save()
            
            # GERAR PDF DE ACERTO DE CONTAS
            try:
                resultado_pdf = indexar_acerto(
                    itensContinuam=itens_continuam,
                    itensRemovidos=produtos_removidos,
                    acaoFinal=acao_final,
                    remessaID=remessa_id
                )
                
                # Verificar se o PDF foi gerado com sucesso
                if 'pdf_base64' in resultado_pdf:
                    return JsonResponse({
                        'status': 'success', 
                        'message': 'Acerto de contas realizado com sucesso!',
                        'pdf_base64': resultado_pdf['pdf_base64'],
                        'nome_arquivo': resultado_pdf['nome_arquivo']
                    })
                else:
                    # Se houve erro na geração do PDF, retornar apenas sucesso da operação
                    return JsonResponse({
                        'status': 'success', 
                        'message': 'Acerto realizado, mas houve erro na geração do recibo.',
                        'pdf_error': resultado_pdf.get('error', 'Erro desconhecido')
                    })
                    
            except Exception as pdf_error:
                # Se a geração do PDF falhar, ainda retornar sucesso da operação principal
                return JsonResponse({
                    'status': 'success', 
                    'message': 'Acerto realizado, mas houve erro na geração do recibo.',
                    'pdf_error': str(pdf_error)
                })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Ocorreu um erro: {e}'}, status=500)
    
@csrf_exempt
def gerar_recibo_pdf_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            produtos = data.get('produtos', [])
            nome_cliente = data.get('nome_cliente', 'Cliente Desconhecido')
            remessaID = data.get('remessaID', None)
            tipoRemessa = str(data.get('tipoRemessa', 'NAO RECEBIDO'))  # 'VENDA' ou 'CONSIGNADO'
            if tipoRemessa == 'CONSIGNADO':
                tipoRemessa = 'EM ABERTO'

            remessa = Remessa.objects.get(id=remessaID) if remessaID else None
            data_saida = remessa.data_saida.strftime('%d/%m/%Y') if remessa and remessa.data_saida else 'N/A'

            count = 1
            my_prod = {}
            my_sale = {}
            codigo_barras = []
            for i in produtos:
                nome_produto = i['nome']
                produto = Produto.objects.get(nome=i['nome'])
                quantidade = i['quantidade']
                preco_unitario = i['preco_unitario']

                temp_list = [nome_produto, float(preco_unitario)]

                my_prod[count] = temp_list
                my_sale[count] = int(quantidade)
                codigo_barras.append(produto.codigo_barras)
                count += 1
            
            resultado = gerar_recibo_pdf_func(
                my_prod=my_prod,
                my_sale=my_sale,
                codigo_barras=codigo_barras,
                nome_cliente=nome_cliente,
                data_nota=data_saida,
                remessa_id=remessaID,
                situacao= tipoRemessa,
                retornar_bytes=True
            )

            # Retornar PDF como base64 para o JavaScript
            return JsonResponse({
                'success': True,
                'pdf_base64': resultado['pdf_base64'],
                'nome_arquivo': resultado['nome_arquivo']
            })
            

        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
        
    return JsonResponse({'success': False, 'error': 'Método não permitido'})
        
            