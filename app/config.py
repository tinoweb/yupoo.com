# config.py
import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # Configurações do PostgreSQL
    DATABASE_URL: Optional[str] = None
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "tinoweb"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: str = "5432"
    POSTGRES_DB: str = "yupoo_db"

    # Configurações do Redis/Celery
    REDIS_URL: Optional[str] = None
    CELERY_BROKER_URL: Optional[str] = None
    CELERY_RESULT_BACKEND: Optional[str] = None

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
    ENVIRONMENT: str = "production"

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
            if not self.CELERY_BROKER_URL:
                self.CELERY_BROKER_URL = self.REDIS_URL
            if not self.CELERY_RESULT_BACKEND:
                self.CELERY_RESULT_BACKEND = self.REDIS_URL

# Configurações de codificação
os.environ["PYTHONIOENCODING"] = "utf-8"
os.environ["LANG"] = "pt_BR.UTF-8"

# Criar instância das configurações
settings = Settings()