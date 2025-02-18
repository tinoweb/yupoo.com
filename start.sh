#!/bin/bash

# Função de log
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*"
}

# Iniciar Xvfb
log "Iniciando Xvfb"
Xvfb :99 -screen 0 1280x1024x24 > /dev/null 2>&1 &

# Aguardar Xvfb iniciar
sleep 1

# Definir porta padrão se não estiver definida
export PORT=${PORT:-10000}
log "Porta definida como $PORT"

# Função para extrair informações do banco de dados
parse_database_url() {
    local db_url="$1"
    local pattern="postgres://([^:]+):([^@]+)@([^:]+):([^/]+)/(.+)"
    
    if [[ $db_url =~ $pattern ]]; then
        DB_USER="${BASH_REMATCH[1]}"
        DB_PASS="${BASH_REMATCH[2]}"
        DB_HOST="${BASH_REMATCH[3]}"
        DB_PORT="${BASH_REMATCH[4]}"
        DB_NAME="${BASH_REMATCH[5]}"
        
        echo "Parsed Database URL:"
        echo "  User: $DB_USER"
        echo "  Host: $DB_HOST"
        echo "  Port: $DB_PORT"
        echo "  Database: $DB_NAME"
    else
        log "Erro: Não foi possível parsear a URL do banco de dados"
        return 1
    fi
}

# Função para verificar conexão com PostgreSQL
check_postgres() {
    local db_url="$1"
    local max_retries=60
    local retry_interval=5
    local retry_count=0

    # Parsear URL do banco de dados
    parse_database_url "$db_url"

    log "Iniciando verificação de conexão com PostgreSQL"
    
    while [ $retry_count -lt $max_retries ]; do
        log "Tentativa de conexão $((retry_count+1))/$max_retries"
        
        # Tentar conexão usando psql
        PGPASSWORD="$DB_PASS" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "SELECT 1" > /dev/null 2>&1
        
        if [ $? -eq 0 ]; then
            log "Conexão com PostgreSQL estabelecida com sucesso!"
            return 0
        fi
        
        # Verificar se o host e porta estão corretos
        nc -z -w5 "$DB_HOST" "$DB_PORT" > /dev/null 2>&1
        if [ $? -ne 0 ]; then
            log "Erro: Não foi possível conectar ao host $DB_HOST na porta $DB_PORT"
        fi
        
        retry_count=$((retry_count+1))
        sleep $retry_interval
    done

    log "Erro: Falha ao conectar ao PostgreSQL após $max_retries tentativas"
    return 1
}

# Verificar conexão com PostgreSQL
if ! check_postgres; then
    echo "Failed to connect to PostgreSQL. Starting application anyway..."
fi

# Iniciar a aplicação
log "Iniciando Gunicorn na porta $PORT"
exec gunicorn app.main:app \
    --bind "0.0.0.0:$PORT" \
    --workers 1 \
    --worker-class uvicorn.workers.UvicornWorker \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level info
