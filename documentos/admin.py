from django.contrib import admin
from .models import Documento, DadosExtraidos

class DadosInline(admin.StackedInline):
    model = DadosExtraidos
    can_delete = False

@admin.register(Documento)
class DocumentoAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'status', 'data_upload')
    list_filter = ('status', 'data_upload')
    search_fields = ('usuario__username', 'mensagem_erro')
    inlines = [DadosInline]

@admin.register(DadosExtraidos)
class DadosAdmin(admin.ModelAdmin):
    list_display = ('numero_nota', 'nome_emitente', 'cnpj_emitente', 'valor_total')
    search_fields = ('numero_nota', 'nome_emitente', 'cnpj_emitente', 'chave_acesso')
