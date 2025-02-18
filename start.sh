#!/bin/bash

# Função de log
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*"
}

# Função de erro
error() {
    echo "[ERROR] $*" >&2
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
    
    log "URL do banco de dados recebida: $db_url"
    
    # Usar sed para extrair partes da URL
    local user=$(echo "$db_url" | sed -E 's|postgres://([^:]+):.*|\1|')
    local password=$(echo "$db_url" | sed -E 's|postgres://[^:]+:([^@]+).*|\1|')
    local host=$(echo "$db_url" | sed -E 's|postgres://[^:]+:[^@]+@([^:]+).*|\1|')
    local port=$(echo "$db_url" | sed -E 's|postgres://[^:]+:[^@]+@[^:]+:([^/]+).*|\1|')
    local database=$(echo "$db_url" | sed -E 's|postgres://[^:]+:[^@]+@[^:]+:[^/]+/(.+)|\1|')
    
    # Validar parâmetros extraídos
    if [ -z "$user" ] || [ -z "$password" ] || [ -z "$host" ] || [ -z "$port" ] || [ -z "$database" ]; then
        error "Não foi possível parsear completamente a URL do banco de dados"
        return 1
    fi
    
    # Exportar variáveis para uso posterior
    export POSTGRES_USER="$user"
    export POSTGRES_PASSWORD="$password"
    export POSTGRES_HOST="$host"
    export POSTGRES_PORT="$port"
    export POSTGRES_DB="$database"
    
    log "Parsed Database URL:"
    log "  User: $POSTGRES_USER"
    log "  Host: $POSTGRES_HOST"
    log "  Port: $POSTGRES_PORT"
    log "  Database: $POSTGRES_DB"
    
    return 0
}

# Função para verificar conexão com PostgreSQL
check_postgres() {
    local db_url="$1"
    local max_retries=60
    local retry_interval=5
    local retry_count=0

    # Parsear URL do banco de dados
    if ! parse_database_url "$db_url"; then
        error "Falha ao parsear URL do banco de dados"
        return 1
    fi

    log "Iniciando verificação de conexão com PostgreSQL"
    
    while [ $retry_count -lt $max_retries ]; do
        log "Tentativa de conexão $((retry_count+1))/$max_retries"
        
        # Verificar se as variáveis foram corretamente definidas
        if [ -z "$POSTGRES_HOST" ] || [ -z "$POSTGRES_PORT" ] || [ -z "$POSTGRES_USER" ] || [ -z "$POSTGRES_DB" ]; then
            error "Variáveis de conexão não definidas corretamente"
            return 1
        fi
        
        # Tentar conexão usando psql
        PGPASSWORD="$POSTGRES_PASSWORD" psql -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "SELECT 1" > /dev/null 2>&1
        
        if [ $? -eq 0 ]; then
            log "Conexão com PostgreSQL estabelecida com sucesso!"
            return 0
        fi
        
        # Verificar se o host e porta estão corretos
        nc -z -w5 "$POSTGRES_HOST" "$POSTGRES_PORT" > /dev/null 2>&1
        if [ $? -ne 0 ]; then
            log "Erro: Não foi possível conectar ao host $POSTGRES_HOST na porta $POSTGRES_PORT"
        fi
        
        retry_count=$((retry_count+1))
        sleep $retry_interval
    done

    error "Falha ao conectar ao PostgreSQL após $max_retries tentativas"
    return 1
}

# Verificar variáveis de ambiente
log "Variáveis de ambiente para conexão:"
log "DATABASE_URL: ${DATABASE_URL:-NÃO DEFINIDA}"
log "POSTGRES_HOST: ${POSTGRES_HOST:-NÃO DEFINIDA}"
log "POSTGRES_PORT: ${POSTGRES_PORT:-NÃO DEFINIDA}"
log "POSTGRES_USER: ${POSTGRES_USER:-NÃO DEFINIDA}"
log "POSTGRES_DB: ${POSTGRES_DB:-NÃO DEFINIDA}"

# Tentar conexão com PostgreSQL
if [ -n "$DATABASE_URL" ]; then
    if ! check_postgres "$DATABASE_URL"; then
        log "Continuando inicialização mesmo sem conexão com PostgreSQL"
    fi
else
    error "Variável DATABASE_URL não definida"
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
