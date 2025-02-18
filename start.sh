#!/bin/bash

# Iniciar Xvfb
Xvfb :99 -screen 0 1280x1024x24 > /dev/null 2>&1 &

# Aguardar Xvfb iniciar
sleep 1

# Aguardar o PostgreSQL estar pronto
until PGPASSWORD=$POSTGRES_PASSWORD psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c '\q'; do
  >&2 echo "PostgreSQL is unavailable - sleeping"
  sleep 1
done

>&2 echo "PostgreSQL is up - executing command"

# Iniciar a aplicação
exec gunicorn app.main:app -c gunicorn_config.py --bind 0.0.0.0:$PORT
