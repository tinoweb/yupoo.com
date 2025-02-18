#!/bin/bash

# Iniciar Xvfb
Xvfb :99 -screen 0 1280x1024x24 > /dev/null 2>&1 &

# Aguardar Xvfb iniciar
sleep 1

# Definir porta padrão se não estiver definida
export PORT=${PORT:-8000}

echo "Starting application on port $PORT"

# Função para verificar conexão com PostgreSQL
check_postgres() {
    local retries=30
    local count=0
    
    if [ ! -z "$DATABASE_URL" ]; then
        # Parse DATABASE_URL
        local pattern="postgres://([^:]+):([^@]+)@([^:]+):([^/]+)/(.+)"
        if [[ $DATABASE_URL =~ $pattern ]]; then
            DB_USER="${BASH_REMATCH[1]}"
            DB_PASS="${BASH_REMATCH[2]}"
            DB_HOST="${BASH_REMATCH[3]}"
            DB_PORT="${BASH_REMATCH[4]}"
            DB_NAME="${BASH_REMATCH[5]}"
        else
            echo "Error: Invalid DATABASE_URL format"
            return 1
        fi
    else
        # Usar variáveis de ambiente padrão
        DB_HOST="$POSTGRES_HOST"
        DB_PORT="$POSTGRES_PORT"
        DB_NAME="$POSTGRES_DB"
        DB_USER="$POSTGRES_USER"
        DB_PASS="$POSTGRES_PASSWORD"
    fi

    echo "Waiting for PostgreSQL to become available..."
    until PGPASSWORD=$DB_PASS psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c '\q' > /dev/null 2>&1; do
        echo "PostgreSQL is unavailable - sleeping (attempt $((count+1))/$retries)"
        count=$((count+1))
        if [ $count -eq $retries ]; then
            echo "Error: PostgreSQL connection timeout after $retries attempts"
            return 1
        fi
        sleep 2
    done

    echo "PostgreSQL is up and running!"
    return 0
}

# Verificar conexão com PostgreSQL
if ! check_postgres; then
    echo "Failed to connect to PostgreSQL. Starting application anyway..."
fi

# Iniciar a aplicação
echo "Starting Gunicorn with port $PORT"
exec gunicorn app.main:app \
    --bind "0.0.0.0:$PORT" \
    --workers 1 \
    --worker-class uvicorn.workers.UvicornWorker \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level info
