# config.py
import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # Configurações do PostgreSQL
    DATABASE_URL: Optional[str] = os.getenv('DATABASE_URL', 'postgresql://postgres:yupoo_tinoweb@localhost:5432/yupoo_db')
    POSTGRES_USER: Optional[str] = None
    POSTGRES_PASSWORD: Optional[str] = None
    POSTGRES_HOST: Optional[str] = None
    POSTGRES_PORT: Optional[str] = None
    POSTGRES_DB: Optional[str] = None

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
        
        # Extrair informações da URL do banco de dados
        if self.DATABASE_URL:
            # Usar expressão regular para extrair partes da URL
            import re
            url_pattern = r'postgres://([^:]+):([^@]+)@([^:]+):([^/]+)/(.+)'
            match = re.match(url_pattern, self.DATABASE_URL)
            
            if match:
                self.POSTGRES_USER = match.group(1)
                self.POSTGRES_PASSWORD = match.group(2)
                self.POSTGRES_HOST = match.group(3)
                self.POSTGRES_PORT = match.group(4)
                self.POSTGRES_DB = match.group(5)
            
            # Definir URL do SQLAlchemy
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