# Configurações do Celery

# Redis como broker
broker_url = 'redis://localhost:6379/0'

# Redis como backend para armazenar resultados
result_backend = 'redis://localhost:6379/1'

# Configurações de tarefas
task_serializer = 'json'
result_serializer = 'json'
accept_content = ['json']
timezone = 'America/Sao_Paulo'
enable_utc = True

# Configurações de workers
worker_concurrency = 4  # Número de workers paralelos
worker_prefetch_multiplier = 1  # Controle de carga
worker_max_tasks_per_child = 100  # Reiniciar worker após N tarefas

# Configurações específicas do Redis
broker_transport_options = {
    'visibility_timeout': 3600,  # 1 hora
    'fanout_prefix': True,
    'fanout_patterns': True,
}

# Configurações de retry
task_acks_late = True
task_reject_on_worker_lost = True

# Descoberta automática de tarefas
imports = ('app.tasks',)
