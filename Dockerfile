FROM python:3.11-slim

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Instala Chrome e ChromeDriver com versões específicas
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-chrome.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" | tee /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Instala ChromeDriver versão 121.0.6167.85 (versão estável recente)
RUN wget --no-verbose -O /tmp/chromedriver_linux64.zip "https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/121.0.6167.85/linux64/chromedriver-linux64.zip" \
    && unzip /tmp/chromedriver_linux64.zip -d /tmp/ \
    && mv /tmp/chromedriver-linux64/chromedriver /usr/local/bin/ \
    && rm -rf /tmp/chromedriver_linux64.zip /tmp/chromedriver-linux64 \
    && chmod +x /usr/local/bin/chromedriver

# Define o diretório de trabalho
WORKDIR /app

# Copia os arquivos do projeto
COPY . .

# Instala as dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Cria diretório para as extrações
RUN mkdir -p extractions

# Variáveis de ambiente padrão
ENV DATABASE_URL="sqlite:///./yupoo_extractor.db" \
    SECRET_KEY="your-secret-key-here" \
    CHROME_BINARY_LOCATION="/usr/bin/google-chrome"

# Expõe a porta
EXPOSE 8000

# Comando para iniciar a aplicação
CMD ["python", "-m", "app.main"]
