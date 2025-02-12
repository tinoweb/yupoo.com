FROM python:3.11-slim

WORKDIR /app

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# Copia os arquivos do projeto
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Cria diretórios necessários
RUN mkdir -p static extractions templates

# Configura variáveis de ambiente
ENV PYTHONUNBUFFERED=1
ENV CHROME_BINARY_LOCATION=/usr/bin/chromium
