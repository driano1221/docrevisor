from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.template.loader import render_to_string
from django.http import HttpResponse
from .models import Documento, DadosExtraidos
from .forms import DadosExtraidosForm
from utils.ocr import extrair_texto
from utils.llm import extrair_dados_com_gemini
import csv
import json

@login_required
def upload_documento(request):
    if request.method == 'POST' and request.FILES.get('arquivo'):
        doc = Documento.objects.create(
            usuario=request.user,
            arquivo=request.FILES['arquivo'],
            status='processando'
        )
        
        try:
            texto = extrair_texto(doc.arquivo.path)
            dados_json = extrair_dados_com_gemini(texto)
            
            if dados_json:
                DadosExtraidos.objects.create(
                    documento=doc,
                    chave_acesso=dados_json.get('chave_acesso') or '',
                    numero_nota=dados_json.get('numero_nota') or '',
                    serie=dados_json.get('serie') or '',
                    cfop=dados_json.get('cfop') or '',
                    data_emissao=dados_json.get('data_emissao') or None,
                    valor_total=dados_json.get('valor_total') or 0.0,
                    nome_emitente=dados_json.get('nome_emitente') or '',
                    cnpj_emitente=dados_json.get('cnpj_emitente') or '',
                    municipio_emitente=dados_json.get('municipio_emitente') or '',
                    uf_emitente=dados_json.get('uf_emitente') or '',
                    nome_destinatario=dados_json.get('nome_destinatario') or '',
                    cnpj_destinatario=dados_json.get('cnpj_destinatario') or '',
                    descricao_servico=dados_json.get('descricao_servico') or ''
                )
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
            messages.error(request, "A IA falhou em extrair alguns dados. Preencha manualmente os campos em vermelho.")
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
        'valor_total': valor_total
    })

@login_required
def gerar_pdf(request, doc_id):
    doc = get_object_or_404(Documento, id=doc_id, usuario=request.user, status='aprovado')
    
    try:
        from weasyprint import HTML
        html_string = render_to_string('documentos/pdf_template.html', {'doc': doc})
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="NF_Revisada_{doc.id}.pdf"'
        HTML(string=html_string).write_pdf(response)
        return response
    except Exception as e:
        messages.error(request, f"Erro ao gerar PDF: O servidor não possui as bibliotecas GTK instaladas. Erro: {e}")
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
                d.dados.chave_acesso
            ])
            
    return response
