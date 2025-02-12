import os

# Configurações do Gunicorn
bind = f"0.0.0.0:{os.getenv('PORT', '8000')}"
workers = 4
worker_class = "uvicorn.workers.UvicornWorker"
timeout = 120
keepalive = 5
errorlog = "-"
accesslog = "-"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Configurações adicionais para produção
graceful_timeout = 120
max_requests = 1000
max_requests_jitter = 50
preload_app = True
