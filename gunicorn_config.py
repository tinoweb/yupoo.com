import os

# Configuração do bind
port = int(os.getenv("PORT", "8000"))
bind = f"0.0.0.0:{port}"

# Configuração dos workers
workers = 4
worker_class = "uvicorn.workers.UvicornWorker"

# Timeouts
timeout = 120
keepalive = 5

# Logging
accesslog = "-"
errorlog = "-"
