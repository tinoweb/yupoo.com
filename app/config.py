# config.py
import os
import re
import logging
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
from urllib.parse import urlparse, unquote

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

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

    def _parse_database_url(self, url: str):
        """
        Parse a database URL and extract connection parameters.
        Suporta múltiplos formatos de URL de banco de dados.
        """
        try:
            # Usar urlparse para parsing robusto
            parsed_url = urlparse(url)
            
            # Remover a parte do esquema (postgres://)
            netloc = parsed_url.netloc
            
            # Separar credenciais e host
            if '@' in netloc:
                credentials, host_port = netloc.split('@')
                
                # Decodificar credenciais
                user, password = credentials.split(':')
                user = unquote(user)
                password = unquote(password)
                
                # Separar host e porta
                if ':' in host_port:
                    host, port = host_port.split(':')
                else:
                    host = host_port
                    port = '5432'  # Porta padrão PostgreSQL
                
                # Remover barra inicial do path para obter nome do banco
                database = parsed_url.path.lstrip('/')
                
                return {
                    'user': user,
                    'password': password,
                    'host': host,
                    'port': port,
                    'database': database
                }
            
            # Caso não tenha credenciais
            return None
        
        except Exception as e:
            logger.error(f"Erro ao parsear URL do banco de dados: {e}")
            return None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        logger.info(f"Inicializando configurações do ambiente: {self.ENVIRONMENT}")
        
        # Tentar parsear a URL do banco de dados
        if self.DATABASE_URL:
            logger.info(f"Parseando URL do banco de dados: {self.DATABASE_URL}")
            db_params = self._parse_database_url(self.DATABASE_URL)
            
            if db_params:
                self.POSTGRES_USER = db_params['user']
                self.POSTGRES_PASSWORD = db_params['password']
                self.POSTGRES_HOST = db_params['host']
                self.POSTGRES_PORT = db_params['port']
                self.POSTGRES_DB = db_params['database']
                
                # Definir URL do SQLAlchemy
                self.SQLALCHEMY_DATABASE_URL = self.DATABASE_URL
                
                logger.info(f"Configurações de banco de dados parseadas com sucesso:")
                logger.info(f"Host: {self.POSTGRES_HOST}")
                logger.info(f"Porta: {self.POSTGRES_PORT}")
                logger.info(f"Banco de dados: {self.POSTGRES_DB}")
            else:
                logger.error("Erro: Não foi possível parsear a URL do banco de dados")

        # Configurar URLs do Redis/Celery
        if self.REDIS_URL:
            logger.info(f"Configurando URLs do Redis: {self.REDIS_URL}")
            if not self.CELERY_BROKER_URL:
                self.CELERY_BROKER_URL = self.REDIS_URL
            if not self.CELERY_RESULT_BACKEND:
                self.CELERY_RESULT_BACKEND = self.REDIS_URL
            
            logger.info("Configurações do Redis/Celery definidas com sucesso")

        logger.info("Inicialização de configurações concluída")

# Configurações de codificação
os.environ["PYTHONIOENCODING"] = "utf-8"
os.environ["LANG"] = "pt_BR.UTF-8"

# Criar instância das configurações
settings = Settings()