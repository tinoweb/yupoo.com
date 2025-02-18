# core/celery.py
from celery import Celery
from .config import settings
import os

# Criar aplicação Celery
app = Celery('yupoo_extractor')

# Configurações básicas do Celery
celery_config = {
    'broker_url': settings.CELERY_BROKER_URL or settings.REDIS_URL,
    'result_backend': settings.CELERY_RESULT_BACKEND or settings.REDIS_URL,
    'task_serializer': 'json',
    'result_serializer': 'json',
    'accept_content': ['json'],
    'timezone': 'America/Sao_Paulo',
    'enable_utc': True,
    'worker_concurrency': 1,
    'task_track_started': True,
    'task_time_limit': 1800,  # 30 minutos
    'task_soft_time_limit': 1500,  # 25 minutos
    'worker_max_tasks_per_child': 50,
    'worker_prefetch_multiplier': 1
}

# Aplicar configurações
app.conf.update(celery_config)

# Descobrir tarefas automaticamente
app.autodiscover_tasks(['app.tasks'])

if __name__ == '__main__':
    app.start()
