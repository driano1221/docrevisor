# DocRevisor: Human-in-the-Loop Document Processing

O **DocRevisor** é uma aplicação web focada no processamento inteligente de documentos fiscais brasileiros. Utiliza visão computacional e IA (Google Gemini) para extrair dados brutos e oferece uma interface de revisão humana para garantir 100% de acurácia antes da aprovação final.

---

## O que o projeto faz

O sistema automatiza o pipeline de recebimento de Notas Fiscais:

1. **Upload** — Recebe PDFs digitais ou imagens escaneadas (PNG, JPG).
2. **Extração com IA** — Para imagens, envia diretamente ao Gemini Vision (multimodal). Para PDFs com texto, extrai via `pdfplumber` e envia ao Gemini texto. Suporta NF-e, NFS-e e CT-e.
3. **Sanitização automática** — CNPJ limpo (14 dígitos), valor monetário normalizado, datas aceitas em múltiplos formatos.
4. **Revisão humana** — Interface de edição de todos os campos extraídos antes de aprovar.
5. **Exportação** — Geração de PDF do comprovante de revisão e exportação em CSV.
6. **Dashboard** — Histórico de documentos, total aprovado e valor acumulado por usuário.

---

## Stack

| Camada | Tecnologia |
|---|---|
| Backend | Django 5.x (Python) |
| IA / Visão | Google Gemini 2.5 Flash (texto e imagem) |
| Extração PDF | pdfplumber |
| OCR fallback | Pytesseract (Tesseract 5) |
| Geração de PDF | xhtml2pdf (puro Python, sem dependências de sistema) |
| Banco de dados | SQLite (dev) / PostgreSQL (prod) |
| Frontend | Bootstrap 5 |

---

## Estrutura do projeto

```
docrevisor/
├── documentos/
│   ├── models.py          # Documento + DadosExtraidos
│   ├── views.py           # Upload, revisão, PDF, CSV
│   ├── forms.py           # Formulário de revisão
│   └── templates/
│       └── documentos/
│           ├── upload.html
│           ├── revisar.html
│           ├── historico.html
│           └── pdf_template.html
├── utils/
│   ├── ocr.py             # Extração de texto de PDFs
│   └── llm.py             # Integração com Gemini (texto e visão)
├── docrevisor/
│   └── settings.py
├── requirements.txt
└── manage.py
```

---

## Como rodar localmente

### Pré-requisitos

- Python 3.10+
- Tesseract OCR instalado no sistema
  - Windows: [tesseract-ocr.github.io](https://tesseract-ocr.github.io/tessdoc/Installation.html)
  - Linux: `sudo apt install tesseract-ocr tesseract-ocr-por`
- Chave de API do Google Gemini

### Instalação

```bash
git clone https://github.com/driano1221/docrevisor.git
cd docrevisor

pip install -r requirements.txt
```

### Configuração

Crie um arquivo `.env` na raiz do projeto:

```env
GEMINI_API_KEY=sua_chave_aqui
SECRET_KEY=sua_secret_key_django
DEBUG=True
```

### Banco de dados e usuário

```bash
python manage.py migrate
python manage.py createsuperuser
```

### Iniciar

```bash
python manage.py runserver 8001
```

Acesse em `http://127.0.0.1:8001/`

---

## Fluxo de processamento

```
Arquivo enviado
     │
     ├── .png / .jpg / .jpeg ──► Gemini Vision (imagem direta)
     │
     └── .pdf ──► pdfplumber ──► texto ──► Gemini texto
                                    │
                           _sanitizar()
                                    │
                           ┌────────────────┐
                           │  CNPJ: 14 dig  │
                           │  Valor: Decimal │
                           │  Data: ISO date │
                           │  UF: 2 letras  │
                           └────────────────┘
                                    │
                           DadosExtraidos salvo
                                    │
                           Revisão humana
                                    │
                           Aprovado → PDF / CSV
```

---

## Decisões técnicas notáveis

**Gemini Vision em vez de Tesseract para imagens**
Tesseract perdia qualidade em imagens de baixa resolução ou com layout complexo (NFS-e prefeitura, por exemplo). Enviar a imagem diretamente ao Gemini Vision retorna dados estruturados com precisão muito superior.

**xhtml2pdf em vez de WeasyPrint**
WeasyPrint exige bibliotecas GTK do sistema operacional, o que inviabiliza o uso em Windows sem instalação manual de dependências nativas. O xhtml2pdf é puro Python e funciona em qualquer plataforma sem configuração adicional.

**Sanitização centralizada (`_sanitizar`)**
Toda limpeza de dados (strip de formatação de CNPJ, normalização de valor monetário, parse de datas em múltiplos formatos) ocorre em uma única função antes de qualquer escrita no banco, evitando erros de integridade e campos truncados.

**Prompt unificado NF-e / NFS-e**
O prompt instrui o modelo a mapear "Prestador" para emitente e "Tomador" para destinatário, tornando o sistema agnóstico ao tipo de documento fiscal.

---

## Roadmap

- [ ] Processamento assíncrono com Celery + Redis (evitar timeout em uploads grandes)
- [ ] Suporte a PDFs baseados em imagem (converter página para imagem e enviar ao Gemini Vision)
- [ ] Gráficos de série temporal de gastos por período
- [ ] Multi-tenancy por organização/empresa
- [ ] Deploy com CI/CD no Render ou Railway

---

*Desenvolvido com Django e Google Gemini.*
