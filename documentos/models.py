from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal

class Documento(models.Model):
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('processando', 'Processando'),
        ('aguardando_revisao', 'Aguardando Revisão'),
        ('aprovado', 'Aprovado'),
        ('erro', 'Erro'),
    ]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    arquivo = models.FileField(upload_to='documentos/%Y/%m/%d/')
    data_upload = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente')
    mensagem_erro = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Doc {self.id} - {self.usuario.username} ({self.status})"

class DadosExtraidos(models.Model):
    documento = models.OneToOneField(Documento, on_delete=models.CASCADE, related_name='dados')
    
    chave_acesso = models.CharField(max_length=44, blank=True)
    numero_nota = models.CharField(max_length=20, blank=True)
    serie = models.CharField(max_length=10, blank=True)
    cfop = models.CharField(max_length=10, blank=True)
    
    data_emissao = models.DateField(null=True, blank=True)
    valor_total = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    
    nome_emitente = models.CharField(max_length=255, blank=True)
    cnpj_emitente = models.CharField(max_length=14, blank=True)
    municipio_emitente = models.CharField(max_length=100, blank=True)
    uf_emitente = models.CharField(max_length=2, blank=True)
    
    nome_destinatario = models.CharField(max_length=255, blank=True)
    cnpj_destinatario = models.CharField(max_length=14, blank=True)
    
    descricao_servico = models.TextField(blank=True)

    def __str__(self):
        return f"Dados da NF {self.numero_nota} - {self.nome_emitente}"
