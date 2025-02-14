#!/bin/bash

# Iniciar Xvfb
Xvfb :99 -screen 0 1280x1024x24 > /dev/null 2>&1 &

# Aguardar Xvfb iniciar
sleep 1

# Iniciar a aplicação
exec gunicorn app.main:app -c gunicorn_config.py
