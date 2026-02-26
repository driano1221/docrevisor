import pdfplumber
import pytesseract
from PIL import Image
import io
import os
import sys

# Caminho padrão do Tesseract no Windows
if sys.platform == 'win32':
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extrair_texto(caminho_arquivo):
    texto = ""
    extensao = caminho_arquivo.lower()

    if extensao.endswith('.pdf'):
        with pdfplumber.open(caminho_arquivo) as pdf:
            for pagina in pdf.pages:
                page_text = pagina.extract_text()
                if page_text:
                    texto += page_text + "\n"
            
    elif extensao.endswith(('.png', '.jpg', '.jpeg')):
        texto = pytesseract.image_to_string(Image.open(caminho_arquivo))
        
    return texto
