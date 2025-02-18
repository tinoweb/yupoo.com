# core/celery.py
from celery import Celery
from .config import settings
import os
import logging
from kombu import Queue, Exchange

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Criar aplicação Celery
app = Celery('yupoo_extractor')

# Log das configurações de conexão
logger.info(f"CELERY_BROKER_URL: {settings.CELERY_BROKER_URL}")
logger.info(f"CELERY_RESULT_BACKEND: {settings.CELERY_RESULT_BACKEND}")
logger.info(f"REDIS_URL: {settings.REDIS_URL}")

# Definir exchanges e filas
default_exchange = Exchange('default', type='direct')
extraction_exchange = Exchange('extraction', type='direct')

# Configurações básicas do Celery
celery_config = {
    # Configurações de broker e backend
    'broker_url': settings.CELERY_BROKER_URL or settings.REDIS_URL,
    'result_backend': settings.CELERY_RESULT_BACKEND or settings.REDIS_URL,
    
    # Serialização
    'task_serializer': 'json',
    'result_serializer': 'json',
    'accept_content': ['json'],
    
    # Timezone e UTC
    'timezone': 'America/Sao_Paulo',
    'enable_utc': True,
    
    # Configurações de worker
    'worker_concurrency': int(os.getenv('CELERY_WORKER_CONCURRENCY', 1)),
    'worker_prefetch_multiplier': 1,
    'worker_max_tasks_per_child': 50,
    
    # Configurações de tarefa
    'task_track_started': True,
    'task_time_limit': 1800,  # 30 minutos
    'task_soft_time_limit': 1500,  # 25 minutos
    'task_acks_late': True,
    'task_reject_on_worker_lost': True,
    
    # Configurações de fila
    'task_queues': (
        Queue('default', default_exchange, routing_key='default'),
        Queue('extraction', extraction_exchange, routing_key='extraction'),
    ),
    'task_default_queue': 'default',
    'task_default_exchange': 'default',
    'task_default_routing_key': 'default',
    
    # Retry
    'task_retry_max_times': 3,
    'task_retry_delay': 60,  # 1 minuto entre retentativas
    
    # Logging e monitoramento
    'worker_log_format': '[%(asctime)s: %(levelname)s/%(processName)s] %(message)s',
    'worker_task_log_format': '[%(asctime)s: %(levelname)s/%(processName)s][%(task_name)s(%(task_id)s)] %(message)s',
    
    # Configurações de conexão do Redis
    'redis_socket_timeout': 30,
    'redis_socket_connect_timeout': 10,
    'redis_max_connections': 10,
    'redis_backend_use_ssl': True
}

# Aplicar configurações
app.conf.update(celery_config)

# Configurar roteamento de tarefas
app.conf.task_routes = {
    'app.tasks.extract_yupoo_data': {
        'queue': 'extraction',
        'routing_key': 'extraction'
    }
}

# Descobrir tarefas automaticamente
app.autodiscover_tasks(['app.tasks'])

# Logging de inicialização
logger.info("Celery app configurado com sucesso")

if __name__ == '__main__':
    app.start()
