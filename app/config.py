# config.py
import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional, List
from datetime import timedelta

class Settings(BaseSettings):
    # Configurações do PostgreSQL
    DATABASE_URL: Optional[str] = None
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "tinoweb"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: str = "5432"
    POSTGRES_DB: str = "yupoo_db"

    # Configurações do Redis
    REDIS_URL: Optional[str] = None
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None

    # Configurações do Celery
    CELERY_BROKER_URL: Optional[str] = None
    CELERY_RESULT_BACKEND: Optional[str] = None
    CELERY_TIMEZONE: str = "America/Sao_Paulo"
    CELERY_TASK_SERIALIZER: str = "json"
    CELERY_RESULT_SERIALIZER: str = "json"
    CELERY_ACCEPT_CONTENT: List[str] = ["json"]
    CELERY_TASK_TRACK_STARTED: bool = True
    CELERY_TASK_TIME_LIMIT: int = 30 * 60  # 30 minutos
    CELERY_TASK_SOFT_TIME_LIMIT: int = 25 * 60  # 25 minutos
    CELERY_WORKER_CONCURRENCY: int = 1  # Para o plano free do Render
    CELERY_WORKER_MAX_TASKS_PER_CHILD: int = 50
    CELERY_WORKER_PREFETCH_MULTIPLIER: int = 1

    # Configurações do SQLAlchemy
    SQLALCHEMY_DATABASE_URL: Optional[str] = None
    SQLALCHEMY_POOL_SIZE: int = 5
    SQLALCHEMY_MAX_OVERFLOW: int = 10
    SQLALCHEMY_ECHO: bool = False

    # Configurações da aplicação
    APP_NAME: str = "Yupoo Scraper"
    API_PREFIX: str = "/api/v1"
    DEBUG: bool = False
    SECRET_KEY: str = "meu_codigo_secreto_aqui_tinoweb"

    # Configurações de ambiente
    ENVIRONMENT: str = "production"
    WORKER_CONCURRENCY: int = 1  # Para o plano free do Render

    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file=".env",
        env_file_encoding="utf-8",
        extra="allow"
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Configurar URLs do banco de dados
        if self.DATABASE_URL:
            self.SQLALCHEMY_DATABASE_URL = self.DATABASE_URL
        else:
            self.SQLALCHEMY_DATABASE_URL = f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
            self.DATABASE_URL = self.SQLALCHEMY_DATABASE_URL

        # Configurar URLs do Redis/Celery
        if self.REDIS_URL:
            self.CELERY_BROKER_URL = self.REDIS_URL
            self.CELERY_RESULT_BACKEND = self.REDIS_URL
        else:
            redis_url = f"redis://{':' + self.REDIS_PASSWORD + '@' if self.REDIS_PASSWORD else ''}{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
            self.CELERY_BROKER_URL = redis_url
            self.CELERY_RESULT_BACKEND = redis_url

# Configurações de codificação
os.environ["PYTHONIOENCODING"] = "utf-8"
os.environ["LANG"] = "pt_BR.UTF-8"

# Criar instância das configurações
settings = Settings()