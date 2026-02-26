import json
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def extrair_dados_com_gemini(texto_bruto):
    prompt = f"""
    Analise o texto de uma Nota Fiscal Eletrônica (NF-e) brasileira abaixo e extraia os campos em formato JSON.
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

    Texto:
    {texto_bruto}
    """

    try:
        response = client.models.generate_content(
            model='gemini-2.0-flash-lite',
            contents=prompt,
        )
        clean_json = response.text.replace('```json', '').replace('```', '').strip()
        return json.loads(clean_json)
    except Exception as e:
        print(f"Erro no Gemini: {e}")
        return None
