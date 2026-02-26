import json
import os
import re
from dotenv import load_dotenv
from google import genai
from PIL import Image

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

_PROMPT_CAMPOS = """
Analise este documento fiscal brasileiro (pode ser NF-e, NFS-e, NF de Servicos, CT-e ou similar)
e extraia as informacoes mapeando para os campos abaixo.

REGRAS OBRIGATORIAS:
- Responda APENAS JSON puro. Sem markdown, sem explicacoes, sem texto extra.
- Use null para campos nao encontrados. NUNCA use string vazia ou zeros falsos.
- CNPJ: retorne SOMENTE os 14 digitos numericos (sem pontos, barra ou traco).
  Ex: "12.345.678/0001-90" -> "12345678000190"
- CPF: retorne SOMENTE os 11 digitos numericos.
- Chave NF-e: retorne SOMENTE os 44 digitos numericos, sem espacos.
- data_emissao: formato YYYY-MM-DD. Se encontrar "DD/MM/YYYY" converta.
- valor_total: numero decimal (float). Use ponto como separador decimal.
  Ex: "R$ 1.500,00" -> 1500.0
- Para NFS-e: "Prestador" equivale a "emitente"; "Tomador" equivale a "destinatario".
- numero_nota: apenas o numero, sem zeros nao significativos a esquerda nao.

Campos JSON:
{
  "chave_acesso": "44 digitos ou null",
  "numero_nota": "numero do documento",
  "serie": "serie ou null",
  "cfop": "CFOP ou null (NFS-e nao tem CFOP)",
  "data_emissao": "YYYY-MM-DD ou null",
  "valor_total": 0.00,
  "nome_emitente": "razao social do emitente/prestador",
  "cnpj_emitente": "14 digitos ou null",
  "municipio_emitente": "cidade do emitente",
  "uf_emitente": "UF 2 letras",
  "nome_destinatario": "razao social do destinatario/tomador",
  "cnpj_destinatario": "14 digitos ou null",
  "descricao_servico": "descricao do servico ou produto"
}
"""


def extrair_dados_com_gemini(texto_bruto):
    prompt = f"{_PROMPT_CAMPOS}\n\nTexto do documento:\n{texto_bruto}"
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        clean = response.text.strip()
        # Remove blocos de markdown se presentes
        if clean.startswith('```'):
            clean = re.sub(r'^```[a-z]*\n?', '', clean)
            clean = re.sub(r'\n?```$', '', clean)
        return json.loads(clean)
    except Exception as e:
        print(f"Erro no Gemini: {e}")
        return None


def extrair_dados_com_gemini_visao(caminho_arquivo):
    try:
        imagem = Image.open(caminho_arquivo)
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[imagem, _PROMPT_CAMPOS],
        )
        clean = response.text.strip()
        if clean.startswith('```'):
            clean = re.sub(r'^```[a-z]*\n?', '', clean)
            clean = re.sub(r'\n?```$', '', clean)
        return json.loads(clean)
    except Exception as e:
        print(f"Erro no Gemini Vision: {e}")
        return None
