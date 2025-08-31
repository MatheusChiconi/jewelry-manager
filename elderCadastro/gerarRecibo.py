from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from io import BytesIO
import base64
import datetime

def gerar_recibo_pdf(my_prod: dict, my_sale: dict, codigo_barras: str, nome_cliente: str, situacao: str, data_nota=datetime.datetime.now().strftime("%d-%b-%Y"), cnpj="12345678910", discount_rate=0, tax_rate=0, nome_arquivo='Recibo.pdf', remessa_id="-", retornar_bytes=False):
    """
    Gera um recibo em PDF com os dados fornecidos
    
    Parâmetros:
    - my_prod: dicionário com produtos {id: [nome, preço]}
    - my_sale: dicionário com vendas {id_produto: quantidade}
    - codigo_barras: lista com códigos de barras de 13 dígitos na ordem dos produtos
    - discount_rate: taxa de desconto em % (padrão é 0)
    - tax_rate: taxa de imposto em % (padrão é 0)
    - cnpj: CNPJ da empresa
    - data_nota: data da nota fiscal em string (formato "DD-MMM-YYYY", exemplo: "06-Ago-2025")
    - nome_cliente: nome completo do cliente
    - nome_arquivo: nome do arquivo PDF a ser gerado (padrão é 'Recibo.pdf')
    - remessa_id: ID da remessa (opcional, padrão é "-")
    - retornar_bytes: se True, retorna o PDF como bytes em memória; se False, salva em arquivo (Colocar True no Django)
    - situacao: situação da remessa em string (pode ser 'EM ABERTO' ou 'VENDA')
    
    Retorna:
    - Se retornar_bytes=True: dicionário com 'pdf_bytes' e 'pdf_base64'
    - Se retornar_bytes=False: None (salva arquivo em disco)
    """
    
    # ==================== INÍCIO DA FUNÇÃO DE CABEÇALHO ====================
    def criar_cabecalho(c):
        """
        Cria o cabeçalho da nota fiscal com logo, endereço, data, etc.
        """
        c.translate(inch, inch)
        c.setFont("Helvetica", 14)
        c.setStrokeColorRGB(0, 0, 0)
        c.setFillColorRGB(0, 0, 0)

        # LOGO DA EMPRESA
        # c.drawImage('occhi.jpg', 0*inch, 9.3*inch, width=1.25*inch, height=0.5*inch)

        # INFORMAÇÕES DA EMPRESA (lado esquerdo)
        c.drawString(0, 9*inch, "Loja Nº : 1234, Rua ABCD")
        c.drawString(0, 8.7*inch, "Cidade: Minha Cidade, CEP : 12345")

        # LINHA SEPARADORA
        c.setFillColorRGB(0, 0, 0)
        c.line(0, 8.6*inch, 7*inch, 8.6*inch)

        # INFORMAÇÕES DA NOTA (lado direito)
        c.drawString(5.6*inch, 9.5*inch, f'Remessa ID :{remessa_id}')
        c.drawString(5.6*inch, 9.3*inch, data_nota)
        
        # NOME DO CLIENTE (destacado abaixo da data)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(4.3*inch, 8.7*inch, f'Cliente: {nome_cliente}')
        
        c.setFont("Helvetica", 8)
        c.drawString(3*inch, 9.6*inch, f'CNPJ Nº :{cnpj}')

        # TÍTULO (vazio no momento)
        c.setFillColorRGB(0, 0, 0)
        c.setFont("Helvetica-Bold", 15)
        c.drawString(5.6*inch, 9*inch, situacao) # Onde ficava escrito "NOTA FISCAL"

        # MARCA D'ÁGUA
        c.rotate(45)
        c.setFillColorCMYK(0, 0, 0, 0.05)  # Transparência
        c.setFont("Times-Bold", 140)
        c.drawString(2*inch, 0.5*inch, "RECIBO")
        c.rotate(-45)

        # CABEÇALHOS DAS COLUNAS
        c.setFillColorRGB(0, 0, 0)
        c.setFont("Helvetica", 14)
        c.drawString(0.1*inch, 8.3*inch, 'Código')
        c.drawString(1.5*inch, 8.3*inch, 'Produtos')
        c.drawString(4.65*inch, 8.3*inch, 'Preço')
        c.drawString(5.43*inch, 8.3*inch, 'Qtd')
        c.drawString(6.22*inch, 8.3*inch, 'Total')

        return c
    # ==================== FIM DA FUNÇÃO DE CABEÇALHO ====================

    # ==================== INÍCIO DA CRIAÇÃO DO PDF ====================
    # Criar buffer em memória se retornar_bytes=True, senão usar arquivo
    if retornar_bytes:
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
    else:
        c = canvas.Canvas(nome_arquivo, pagesize=letter)
    
    c = criar_cabecalho(c)

    # ==================== INÍCIO DO PROCESSAMENTO DOS PRODUTOS ====================
    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica", 10)  # Fonte menor: de 20 para 10
    row_gap = 0.14  # Espaçamento menor: de 0.3 para 0.14
    line_y = 7.9   # Posição Y inicial
    total = 0      # Total geral
    row_counter = 0      # Contador para faixas alternadas
    items_per_page = 50  # Aumentado: de 20 para 46 produtos por página
    current_item = 0     # Contador de itens na página atual

    # Converter my_sale para lista para paginação
    sale_items = list(my_sale.items())

    # LOOP PRINCIPAL - PROCESSAR CADA PRODUTO
    for i, (item_id, quantity) in enumerate(sale_items):
        if quantity == 0:
            continue
            
        # VERIFICAR SE PRECISA CRIAR NOVA PÁGINA
        if current_item >= items_per_page and i < len(sale_items):
            c.showPage()  # Finalizar página atual
            c = criar_cabecalho(c)  # Criar nova página com cabeçalho
            c.setFillColorRGB(0, 0, 0)
            c.setFont("Helvetica", 10)  # Fonte pequena nas páginas seguintes
            line_y = 7.9  # Reset posição vertical
            current_item = 0  # Reset contador de itens
        
        # DESENHAR FAIXA CINZA ALTERNADA (zebra striping)
        if row_counter % 2 == 0:  # Linhas pares (0, 2, 4, ...)
            c.setFillColorRGB(0.9, 0.9, 0.9)  # Cinza claro
            c.rect(0, (line_y-0.02)*inch, 7*inch, 0.15*inch, fill=1, stroke=0)  # Faixa menor
        
        # DESENHAR INFORMAÇÕES DO PRODUTO
        c.setFillColorRGB(0, 0, 0)  # Voltar para cor preta
        c.setFont("Helvetica", 10)  # Garantir fonte pequena
        
        # Código de barras (13 dígitos)
        codigo = codigo_barras[i] if i < len(codigo_barras) else "0000000000000"
        c.drawString(0.1*inch, line_y*inch, str(codigo))
        
        # Nome do produto - verificar se começa com "~" para riscar
        nome_produto = str(my_prod[item_id][0])
        produto_riscado = nome_produto.startswith("~")
        
        if produto_riscado:
            # Remove o "~" do nome para exibição
            nome_produto_display = nome_produto[1:]
        else:
            nome_produto_display = nome_produto
            
        c.drawString(1.5*inch, line_y*inch, nome_produto_display)
        
        # Se o produto está riscado, desenhar linha sobre o texto
        if produto_riscado:
            # Calcular largura aproximada do texto para desenhar a linha
            texto_largura = c.stringWidth(nome_produto_display, "Helvetica", 10)
            c.setStrokeColorRGB(0, 0, 0)  # Cor preta para a linha
            c.line(1.5*inch, (line_y + 0.05)*inch, (1.5*inch + texto_largura), (line_y + 0.05)*inch)
        
        # Preço (campo 20% menor) - Se produto riscado, preço = 0
        preco_exibicao = 0.0 if produto_riscado else my_prod[item_id][1]
        c.drawRightString(5.25*inch, line_y*inch, f"{preco_exibicao:.2f}")
        
        # Quantidade (campo metade do tamanho)
        c.drawRightString(5.65*inch, line_y*inch, str(quantity))
        
        # CALCULAR E DESENHAR SUBTOTAL - Se produto riscado, subtotal = 0
        if produto_riscado:
            sub_total = 0.0
        else:
            sub_total = my_prod[item_id][1] * quantity
            
        c.drawRightString(6.85*inch, line_y*inch, f"{sub_total:.2f}")  # Campo total reduzido pela metade
        total = round(total + sub_total, 2)
        
        # AVANÇAR PARA PRÓXIMA LINHA
        line_y = line_y - row_gap
        row_counter += 1
        current_item += 1
    # ==================== FIM DO PROCESSAMENTO DOS PRODUTOS ====================
    # LINHAS VERTICAIS SEPARADORAS
        c.setStrokeColorCMYK(0, 0, 0, 1)
        c.line(1.4*inch, 8.3*inch, 1.4*inch, 1*inch)  # Separador Código/Produtos
        c.line(4.5*inch, 8.3*inch, 4.5*inch, 1*inch)  # Separador Produtos/Preço (movido para direita)
        c.line(5.3*inch, 8.3*inch, 5.3*inch, 1*inch)  # Separador Preço/Quantidade (mantido)
        c.line(5.9*inch, 8.3*inch, 5.9*inch, 1*inch)  # Separador Quantidade/Total (mantido)
        c.line(0.01*inch, 1*inch, 7*inch, 1*inch)   # Linha horizontal mais baixa
    # ==================== INÍCIO DA SEÇÃO DE TOTAIS ====================
    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica", 18)  # Fonte menor para totais

    # FAIXAS CINZAS PARA OS TOTAIS (posições mais baixas e compactas)
    c.setFillColorRGB(0.9, 0.9, 0.9)  # Cinza claro
    c.rect(1*inch, 0.1*inch, 6*inch, 0.25*inch, fill=1, stroke=0)  # Desconto
    c.rect(1*inch, -0.2*inch, 6*inch, 0.25*inch, fill=1, stroke=0)  # Imposto
    c.rect(1*inch, -0.5*inch, 6*inch, 0.25*inch, fill=1, stroke=0)  # Total

    # TEXTOS DOS TOTAIS
    c.setFillColorRGB(0, 0, 0)
    c.drawString(1*inch, 0.1*inch, 'Desconto')
    c.drawString(1*inch, -0.2*inch, 'Imposto')
    c.setFont("Helvetica-Bold", 18)
    c.drawString(1*inch, -0.5*inch, 'Total')

    # TOTAL DE ITENS E SUBTOTAL (posição mais baixa) - Excluir produtos riscados
    total_quantity = 0
    for item_id, quantity in my_sale.items():
        # Verificar se o produto não está riscado (não começa com "~")
        nome_produto = str(my_prod[item_id][0])
        if not nome_produto.startswith("~"):
            total_quantity += quantity
    
    c.setFont("Helvetica", 14)
    c.drawString(0.1*inch, 0.75*inch, f'Total de Itens: {total_quantity}')
    c.drawString(5*inch, 0.75*inch, 'Subtotal:')

    # CÁLCULOS E VALORES DOS TOTAIS
    c.setFont("Helvetica", 18)
    c.drawRightString(6.85*inch, 0.75*inch, f"{float(total):.2f}")  # Subtotal
    
    # DESCONTO
    discount = round((discount_rate / 100) * total, 2)
    c.drawRightString(4*inch, 0.1*inch, str(discount_rate) + '%')
    c.drawRightString(6.85*inch, 0.1*inch, f"-{discount:.2f}")
    
    # IMPOSTO
    tax = round((tax_rate / 100) * (total - discount), 2)
    c.drawRightString(4*inch, -0.2*inch, str(tax_rate) + '%')
    c.drawRightString(6.85*inch, -0.2*inch, f"{tax:.2f}")
    
    # TOTAL FINAL
    total_final = total - discount + tax
    c.setFont("Helvetica-Bold", 18)
    c.setFillColorRGB(0, 0, 0)
    c.drawRightString(6.85*inch, -0.5*inch, f"{total_final:.2f}")
    # ==================== FIM DA SEÇÃO DE TOTAIS ====================

    # ==================== FINALIZAÇÃO DO PDF ====================
    c.showPage()
    c.save()
    
    if retornar_bytes:
        # Retornar PDF como bytes e base64 para uso no Django
        pdf_bytes = buffer.getvalue()
        buffer.close()
        pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
        
        return {
            'pdf_bytes': pdf_bytes,
            'pdf_base64': pdf_base64,
            'nome_arquivo': nome_arquivo
        }
    else:
        print(f"Nota fiscal gerada com sucesso: {nome_arquivo}")
        return None
    # ==================== FIM DA FINALIZAÇÃO ====================

def indexar_acerto(itensContinuam, itensRemovidos, acaoFinal, remessaID):
    """
    Gera um recibo de acerto de contas combinando itens que continuam com o cliente
    e itens que foram removidos (marcados com "~").
    
    Parâmetros:
    - itensContinuam: lista de dicionários com itens que continuam {nome, quantidade, preco_unitario}
    - itensRemovidos: dicionário com produtos removidos {nome_produto: quantidade}
    - acaoFinal: string indicando a ação final ('FECHAR' ou 'ABERTO')
    - remessaID: ID da remessa para buscar dados no banco
    
    Retorna:
    - Dicionário com dados do PDF gerado (pdf_base64, nome_arquivo)
    """
    from produtos.models import Produto
    from clientes.models import Remessa
    
    try:
        # Buscar dados da remessa no banco de dados
        remessa = Remessa.objects.get(id=remessaID) if remessaID else None
        nome_cliente = remessa.cliente.nome_completo if remessa else 'Cliente Desconhecido'
        data_saida = remessa.data_saida.strftime('%d/%m/%Y') if remessa and remessa.data_saida else 'N/A'
        
        # Definir tipo da remessa baseado na ação final
        tipoRemessa = 'FINALIZADO' if acaoFinal == 'FECHAR' else 'EM ABERTO'
        
        # Inicializar contadores e dicionários para a função gerar_recibo_pdf
        count = 1
        my_prod = {}  # {id: [nome_produto, preco]}
        my_sale = {}  # {id: quantidade}
        codigo_barras = []
        
        # PROCESSAR ITENS QUE CONTINUAM COM O CLIENTE
        for item in itensContinuam:
            nome_produto = item['nome']
            quantidade = int(item['quantidade'])
            preco_unitario = float(item['preco_unitario'])
            
            # Buscar código de barras do produto
            try:
                produto = Produto.objects.get(nome=nome_produto)
                codigo_produto = produto.codigo_barras
            except Produto.DoesNotExist:
                codigo_produto = "0000000000000"  # Código padrão se não encontrar
            
            # Adicionar aos dicionários
            temp_list = [nome_produto, preco_unitario]
            my_prod[count] = temp_list
            my_sale[count] = quantidade
            codigo_barras.append(codigo_produto)
            count += 1
        
        # PROCESSAR ITENS REMOVIDOS (COM "~" NO NOME)
        for nome_produto, quantidade in itensRemovidos.items():
            # Adicionar "~" no início do nome para marcar como removido
            nome_produto_riscado = f"~{nome_produto}"
            
            # Buscar dados do produto no banco para pegar preço e código de barras
            try:
                produto = Produto.objects.get(nome=nome_produto)
                preco_unitario = float(produto.preco_venda)
                codigo_produto = produto.codigo_barras
            except Produto.DoesNotExist:
                preco_unitario = 0.0
                codigo_produto = "0000000000000"
            
            # Adicionar aos dicionários com nome riscado
            temp_list = [nome_produto_riscado, preco_unitario]
            my_prod[count] = temp_list
            my_sale[count] = int(quantidade)
            codigo_barras.append(codigo_produto)
            count += 1
        
        # GERAR O PDF USANDO A FUNÇÃO PRINCIPAL
        resultado = gerar_recibo_pdf(
            my_prod=my_prod,
            my_sale=my_sale,
            codigo_barras=codigo_barras,
            nome_cliente=nome_cliente,
            data_nota=data_saida,
            remessa_id=remessaID,
            situacao=tipoRemessa,
            nome_arquivo=f'acerto_remessa_{remessaID}.pdf',
            retornar_bytes=True
        )
        
        return resultado
        
    except Exception as e:
        # Em caso de erro, retornar estrutura de erro
        return {
            'success': False,
            'error': f'Erro ao gerar recibo de acerto: {str(e)}'
        }
