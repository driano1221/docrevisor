import json
import os
from dotenv import load_dotenv
from google import genai
from PIL import Image

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

_PROMPT_CAMPOS = """
    Analise a Nota Fiscal Eletrônica (NF-e) brasileira e extraia os campos em formato JSON.
    Responda APENAS o JSON, sem explicações, sem markdown.
    Campos:
    - chave_acesso (44 dígitos)
    - numero_nota
    - serie
    - cfop
    - data_emissao (formato ISO YYYY-MM-DD)
    - valor_total (float)
    - nome_emitente
    - cnpj_emitente (apenas números)
    - municipio_emitente
    - uf_emitente (2 letras)
    - nome_destinatario
    - cnpj_destinatario (apenas números)
    - descricao_servico
"""

def extrair_dados_com_gemini(texto_bruto):
    prompt = f"{_PROMPT_CAMPOS}\n    Texto:\n    {texto_bruto}"
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        clean_json = response.text.replace('```json', '').replace('```', '').strip()
        return json.loads(clean_json)
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
        clean_json = response.text.replace('```json', '').replace('```', '').strip()
        return json.loads(clean_json)
    except Exception as e:
        print(f"Erro no Gemini Vision: {e}")
        return None
