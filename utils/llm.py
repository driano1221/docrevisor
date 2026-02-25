import google.generativeai as genai
import json
import os
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def extrair_dados_com_gemini(texto_bruto):
    model = genai.GenerativeModel('gemini-2.0-flash')
    
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
        response = model.generate_content(prompt)
        # Limpa possíveis blocos de markdown se a IA ignorar o comando
        clean_json = response.text.replace('```json', '').replace('```', '').strip()
        return json.loads(clean_json)
    except Exception as e:
        print(f"Erro no Gemini: {e}")
        return None
