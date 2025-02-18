import os
import multiprocessing

# Configurações básicas
bind = f"0.0.0.0:{os.getenv('PORT', '8000')}"
workers = 1  # Para plano free do Render, limitamos a 1 worker
worker_class = 'uvicorn.workers.UvicornWorker'
timeout = 120

# Configurações de logging
accesslog = '-'
errorlog = '-'
loglevel = 'info'
capture_output = True
enable_stdio_inheritance = True

# Configurações de reload e debugging
reload = False
reload_extra_files = []
spew = False

# Configurações de processo
daemon = False
raw_env = [
    f"PYTHONPATH={os.getcwd()}"
]

# Configurações de timeout e conexão
graceful_timeout = 120
keep_alive = 5
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50

# Configurações de buffer
forwarded_allow_ips = '*'
proxy_allow_ips = '*'
secure_scheme_headers = {
    'X-FORWARDED-PROTOCOL': 'ssl',
    'X-FORWARDED-PROTO': 'https',
    'X-FORWARDED-SSL': 'on'
}
