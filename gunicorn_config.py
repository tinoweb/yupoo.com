import os

# Configurações básicas
bind = f"0.0.0.0:{os.getenv('PORT', '8000')}"
workers = 1  # Para plano free do Render, limitamos a 1 worker
worker_class = 'uvicorn.workers.UvicornWorker'
timeout = 120

# Configurações de logging
accesslog = '-'
errorlog = '-'
loglevel = 'info'

# Configurações de reload e debugging
reload = False
reload_extra_files = []
spew = False

# Configurações de processo
daemon = False
raw_env = [
    f"PYTHONPATH={os.getcwd()}"
]

# Configurações de timeout
graceful_timeout = 120
keep_alive = 5
