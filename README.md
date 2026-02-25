# 📄 DocRevisor: Human-in-the-Loop Document Processing

O **DocRevisor** é um SaaS (Software as a Service) focado no processamento inteligente de documentos fiscais brasileiros. Ele utiliza Inteligência Artificial (Gemini 2.0) para extrair dados brutos e oferece uma interface de revisão humana para garantir 100% de acurácia.

## 🚀 O que o projeto faz?

O sistema automatiza o pipeline de recebimento de Notas Fiscais Eletrônicas (NF-e):
1.  **Upload:** Recebe PDFs digitais ou imagens escaneadas.
2.  **Extração (OCR + IA):** Lê o texto e usa LLM para transformar caos em JSON estruturado.
3.  **Validação Brasileira:** Valida algoritmicamente CNPJs e chaves de acesso de 44 dígitos.
4.  **Revisão:** Interface para correção humana de campos que a IA não identificou com precisão.
5.  **Analytics:** Dashboard estatístico com média de gastos e volume de processamento.
6.  **Exportação:** Geração de PDFs profissionais (WeasyPrint) e exportação para CSV (Pandas-ready).

## 🛠️ Stack Técnica

- **Backend:** Django 5.x (Python)
- **IA:** Google Gemini 2.0 Flash
- **OCR:** pdfplumber & Pytesseract
- **Estética:** Tipografia estilo *New York Times* com layout *Flashscore* (Bootstrap 5).
- **Dados:** SQLite (Dev) / PostgreSQL (Prod).

## 📂 Como rodar o projeto localmente

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/seu-usuario/docrevisor.git
   cd docrevisor
   ```

2. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure as Variáveis de Ambiente:**
   - Crie um arquivo `.env` na raiz.
   - Adicione sua `GEMINI_API_KEY`.

4. **Prepare o Banco de Dados:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   python manage.py createsuperuser
   ```

5. **Inicie o Servidor:**
   ```bash
   python manage.py runserver 8001
   ```

## 📉 O que falta (Roadmap)

Embora o MVP esteja funcional, os próximos passos para escala são:
- [ ] **Processamento Assíncrono:** Integração com Celery/Redis para evitar timeouts em notas grandes.
- [ ] **Gráficos Avançados:** Implementação de Plotly.js para visualização de séries temporais de gastos.
- [ ] **Multi-tenancy:** Isolamento completo de dados por empresa (Organizações).
- [ ] **Deploy Automatizado:** Configuração de CI/CD para o Render.com.

---
*Desenvolvido como projeto de aprendizado prático em Django e Engenharia de Dados.*
