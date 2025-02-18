# config.py
import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # Configurações do PostgreSQL
    DATABASE_URL: Optional[str] = os.getenv('DATABASE_URL')
    POSTGRES_USER: str = os.getenv('POSTGRES_USER', 'postgres')
    POSTGRES_PASSWORD: str = os.getenv('POSTGRES_PASSWORD', 'yupoo_tinoweb')
    POSTGRES_HOST: str = os.getenv('POSTGRES_HOST', 'localhost')
    POSTGRES_PORT: str = os.getenv('POSTGRES_PORT', '5432')
    POSTGRES_DB: str = os.getenv('POSTGRES_DB', 'yupoo_db')

    # Configurações do Redis/Celery
    REDIS_URL: Optional[str] = os.getenv('REDIS_URL')
    CELERY_BROKER_URL: Optional[str] = os.getenv('CELERY_BROKER_URL')
    CELERY_RESULT_BACKEND: Optional[str] = os.getenv('CELERY_RESULT_BACKEND')

    # Configurações do SQLAlchemy
    SQLALCHEMY_DATABASE_URL: Optional[str] = None
    SQLALCHEMY_POOL_SIZE: int = 5
    SQLALCHEMY_MAX_OVERFLOW: int = 10
    SQLALCHEMY_ECHO: bool = False

    # Configurações da aplicação
    APP_NAME: str = "Yupoo Scraper"
    API_PREFIX: str = "/api/v1"
    DEBUG: bool = os.getenv('DEBUG', 'false').lower() == 'true'
    SECRET_KEY: str = os.getenv('SECRET_KEY', 'meu_codigo_secreto_aqui_tinoweb')
    ENVIRONMENT: str = os.getenv('ENVIRONMENT', 'production')

    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file=".env",
        env_file_encoding="utf-8",
        extra="allow"
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Configurar URLs do banco de dados
        if not self.DATABASE_URL:
            self.DATABASE_URL = f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        
        self.SQLALCHEMY_DATABASE_URL = self.DATABASE_URL

        # Configurar URLs do Redis/Celery
        if self.REDIS_URL:
            if not self.CELERY_BROKER_URL:
                self.CELERY_BROKER_URL = self.REDIS_URL
            if not self.CELERY_RESULT_BACKEND:
                self.CELERY_RESULT_BACKEND = self.REDIS_URL

# Configurações de codificação
os.environ["PYTHONIOENCODING"] = "utf-8"
os.environ["LANG"] = "pt_BR.UTF-8"

# Criar instância das configurações
settings = Settings()