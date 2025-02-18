#!/bin/bash

# Iniciar Xvfb
Xvfb :99 -screen 0 1280x1024x24 > /dev/null 2>&1 &

# Aguardar Xvfb iniciar
sleep 1

# Extrair host e porta do DATABASE_URL
if [ ! -z "$DATABASE_URL" ]; then
    # Extrair informações do DATABASE_URL
    DB_HOST=$(echo $DATABASE_URL | awk -F[@//] '{print $4}' | cut -d: -f1)
    DB_PORT=$(echo $DATABASE_URL | awk -F[@//] '{print $4}' | cut -d: -f2 | cut -d/ -f1)
    DB_NAME=$(echo $DATABASE_URL | awk -F[@//] '{print $4}' | cut -d/ -f2)
    DB_USER=$(echo $DATABASE_URL | awk -F[@//] '{print $3}' | cut -d: -f1)
    DB_PASS=$(echo $DATABASE_URL | awk -F[@//] '{print $3}' | cut -d: -f2)
else
    # Usar variáveis de ambiente padrão
    DB_HOST=$POSTGRES_HOST
    DB_PORT=$POSTGRES_PORT
    DB_NAME=$POSTGRES_DB
    DB_USER=$POSTGRES_USER
    DB_PASS=$POSTGRES_PASSWORD
fi

# Aguardar o PostgreSQL estar pronto
until PGPASSWORD=$DB_PASS psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c '\q' > /dev/null 2>&1; do
    echo "PostgreSQL is unavailable - sleeping"
    sleep 1
done

echo "PostgreSQL is up - executing command"

# Iniciar a aplicação
exec gunicorn app.main:app -c gunicorn_config.py --bind 0.0.0.0:$PORT
