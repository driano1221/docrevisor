import re
import csv
from decimal import Decimal, InvalidOperation
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.template.loader import render_to_string
from django.http import HttpResponse
from .models import Documento, DadosExtraidos
from .forms import DadosExtraidosForm
from utils.ocr import extrair_texto
from utils.llm import extrair_dados_com_gemini, extrair_dados_com_gemini_visao


def _so_digitos(valor, tamanho_max=None):
    """Mantém apenas dígitos numéricos, trunca ao tamanho máximo."""
    if not valor:
        return ''
    resultado = re.sub(r'\D', '', str(valor))
    if tamanho_max:
        resultado = resultado[:tamanho_max]
    return resultado


def _sanitizar(dados_json):
    """Valida e limpa os dados vindos da IA antes de salvar no banco."""
    if not dados_json:
        return {}

    # CNPJ: somente 14 dígitos
    cnpj_emit = _so_digitos(dados_json.get('cnpj_emitente'), 14)
    cnpj_dest = _so_digitos(dados_json.get('cnpj_destinatario'), 14)

    # Chave de acesso NF-e: somente 44 dígitos
    chave = _so_digitos(dados_json.get('chave_acesso'), 44)

    # Valor total: converte para Decimal, aceita vírgula como separador
    valor_raw = str(dados_json.get('valor_total') or '0').replace(',', '.')
    # Remove tudo que não seja dígito nem ponto
    valor_raw = re.sub(r'[^\d.]', '', valor_raw)
    try:
        valor = Decimal(valor_raw)
    except InvalidOperation:
        valor = Decimal('0.00')

    # Data de emissão: aceita YYYY-MM-DD e DD/MM/YYYY
    data_raw = dados_json.get('data_emissao') or ''
    data = None
    if data_raw:
        from datetime import datetime
        for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y', '%Y/%m/%d'):
            try:
                data = datetime.strptime(str(data_raw).strip(), fmt).date()
                break
            except ValueError:
                continue

    # UF: somente 2 letras maiúsculas
    uf = str(dados_json.get('uf_emitente') or '').strip().upper()[:2]

    # Campos de texto: strip simples, null vira ''
    def txt(campo):
        return str(dados_json.get(campo) or '').strip()

    return {
        'chave_acesso':       chave,
        'numero_nota':        txt('numero_nota')[:20],
        'serie':              txt('serie')[:10],
        'cfop':               txt('cfop')[:10],
        'data_emissao':       data,
        'valor_total':        valor,
        'nome_emitente':      txt('nome_emitente')[:255],
        'cnpj_emitente':      cnpj_emit,
        'municipio_emitente': txt('municipio_emitente')[:100],
        'uf_emitente':        uf,
        'nome_destinatario':  txt('nome_destinatario')[:255],
        'cnpj_destinatario':  cnpj_dest,
        'descricao_servico':  txt('descricao_servico'),
    }


@login_required
def upload_documento(request):
    if request.method == 'POST' and request.FILES.get('arquivo'):
        doc = Documento.objects.create(
            usuario=request.user,
            arquivo=request.FILES['arquivo'],
            status='processando'
        )

        try:
            caminho = doc.arquivo.path
            if caminho.lower().endswith(('.png', '.jpg', '.jpeg')):
                dados_json = extrair_dados_com_gemini_visao(caminho)
            else:
                texto = extrair_texto(caminho)
                dados_json = extrair_dados_com_gemini(texto)

            dados = _sanitizar(dados_json)
            if dados:
                DadosExtraidos.objects.create(documento=doc, **dados)
                doc.status = 'aguardando_revisao'
                doc.save()
                return redirect('revisar_documento', doc_id=doc.id)
            else:
                doc.status = 'erro'
                doc.mensagem_erro = "A IA não conseguiu interpretar o documento."
                doc.save()
        except Exception as e:
            doc.status = 'erro'
            doc.mensagem_erro = str(e)
            doc.save()

        return redirect('historico')

    return render(request, 'documentos/upload.html')


@login_required
def revisar_documento(request, doc_id):
    doc = get_object_or_404(Documento, id=doc_id, usuario=request.user)
    dados = getattr(doc, 'dados', None)

    if request.method == 'POST':
        form = DadosExtraidosForm(request.POST, instance=dados)
        if form.is_valid():
            instancia = form.save(commit=False)
            instancia.documento = doc
            instancia.save()
            doc.status = 'aprovado'
            doc.save()
            messages.success(request, "Documento revisado com sucesso!")
            return redirect('historico')
        else:
            messages.error(request, "Preencha manualmente os campos em vermelho.")
    else:
        form = DadosExtraidosForm(instance=dados)

    return render(request, 'documentos/revisar.html', {'form': form, 'doc': doc})


@login_required
def historico(request):
    documentos = Documento.objects.filter(usuario=request.user).order_by('-data_upload')
    aprovados = documentos.filter(status='aprovado')

    total_processado = documentos.count()
    valor_total = sum(d.dados.valor_total for d in aprovados if hasattr(d, 'dados'))

    return render(request, 'documentos/historico.html', {
        'documentos': documentos,
        'total_processado': total_processado,
        'valor_total': valor_total,
    })


@login_required
def gerar_pdf(request, doc_id):
    doc = get_object_or_404(Documento, id=doc_id, usuario=request.user, status='aprovado')

    try:
        from xhtml2pdf import pisa
        from io import BytesIO
        html_string = render_to_string('documentos/pdf_template.html', {'doc': doc})
        buffer = BytesIO()
        pisa.CreatePDF(src=html_string, dest=buffer, encoding='utf-8')
        response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="NF_Revisada_{doc.id}.pdf"'
        return response
    except Exception as e:
        messages.error(request, f"Erro ao gerar PDF: {e}")
        return redirect('historico')


@login_required
def exportar_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="documentos_aprovados.csv"'

    writer = csv.writer(response)
    writer.writerow(['ID', 'Emitente', 'CNPJ', 'Data', 'Valor', 'Chave NF-e'])

    docs = Documento.objects.filter(usuario=request.user, status='aprovado')
    for d in docs:
        if hasattr(d, 'dados'):
            writer.writerow([
                d.id,
                d.dados.nome_emitente,
                d.dados.cnpj_emitente,
                d.dados.data_emissao,
                d.dados.valor_total,
                d.dados.chave_acesso,
            ])

    return response
