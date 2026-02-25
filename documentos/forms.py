from django import forms
from .models import DadosExtraidos
from utils.validators import validar_cnpj, validar_chave_nfe, UFS_VALIDAS
import re

class DadosExtraidosForm(forms.ModelForm):
    class Meta:
        model = DadosExtraidos
        exclude = ['documento']
        widgets = {
            'data_emissao': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'descricao_servico': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if field != 'data_emissao' and field != 'descricao_servico':
                self.fields[field].widget.attrs.update({'class': 'form-control'})

    def clean_cnpj_emitente(self):
        cnpj = re.sub(r'\D', '', self.cleaned_data.get('cnpj_emitente'))
        if cnpj and not validar_cnpj(cnpj):
            raise forms.ValidationError("CNPJ do Emitente inválido.")
        return cnpj

    def clean_cnpj_destinatario(self):
        cnpj = re.sub(r'\D', '', self.cleaned_data.get('cnpj_destinatario'))
        if cnpj and not validar_cnpj(cnpj):
            raise forms.ValidationError("CNPJ do Destinatário inválido.")
        return cnpj

    def clean_chave_acesso(self):
        chave = re.sub(r'\D', '', self.cleaned_data.get('chave_acesso'))
        if chave and not validar_chave_nfe(chave):
            raise forms.ValidationError("Chave de acesso deve ter 44 dígitos.")
        return chave

    def clean_uf_emitente(self):
        uf = self.cleaned_data.get('uf_emitente').upper()
        if uf and uf not in UFS_VALIDAS:
            raise forms.ValidationError("UF inválida.")
        return uf

    def clean_valor_total(self):
        valor = self.cleaned_data.get('valor_total')
        if valor and valor < 0:
            raise forms.ValidationError("O valor total não pode ser negativo.")
        return valor
