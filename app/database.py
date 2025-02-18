import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import SQLAlchemyError, OperationalError
import time

from .config import settings

# Configurar logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configurar base para modelos
Base = declarative_base()

def get_database_url():
    """
    Obtém a URL do banco de dados com tratamento de erros.
    
    Returns:
        str: URL de conexão com o banco de dados
    """
    try:
        # Priorizar variáveis de ambiente do Render
        database_url = os.getenv('DATABASE_URL')
        
        if not database_url:
            # Fallback para configurações locais
            database_url = settings.SQLALCHEMY_DATABASE_URL
        
        logger.info(f"Obtendo URL do banco de dados: {database_url}")
        return database_url
    except Exception as e:
        logger.error(f"Erro ao obter URL do banco de dados: {e}")
        raise

def create_database_engine(max_retries=5, retry_delay=5):
    """
    Cria e retorna um engine SQLAlchemy com tratamento de erros e retentativas.
    
    Args:
        max_retries (int): Número máximo de tentativas de conexão
        retry_delay (int): Tempo de espera entre tentativas em segundos
    
    Returns:
        sqlalchemy.engine.base.Engine: Engine de conexão com o banco de dados
    """
    for attempt in range(1, max_retries + 1):
        try:
            database_url = get_database_url()
            
            # Configurações de pool
            engine = create_engine(
                database_url,
                pool_size=settings.SQLALCHEMY_POOL_SIZE,
                max_overflow=settings.SQLALCHEMY_MAX_OVERFLOW,
                echo=settings.SQLALCHEMY_ECHO,
                pool_pre_ping=True,  # Verificar conexão antes de usar
                pool_recycle=1800,   # Reconectar a cada 30 minutos
            )
            
            # Testar conexão
            with engine.connect() as connection:
                logger.info("Conexão com o banco de dados estabelecida com sucesso!")
                return engine
        
        except (SQLAlchemyError, OperationalError) as e:
            logger.warning(f"Tentativa {attempt}/{max_retries} de conexão com o banco de dados falhou: {e}")
            
            if attempt == max_retries:
                logger.error("Falha definitiva ao conectar ao banco de dados.")
                raise
            
            time.sleep(retry_delay)

# Criar engine de banco de dados
try:
    engine = create_database_engine()

    # Criar sessão
    SessionLocal = sessionmaker(
        autocommit=False, 
        autoflush=False, 
        bind=engine
    )
except Exception as e:
    logger.error(f"Erro crítico ao configurar banco de dados: {e}")
    SessionLocal = None
    engine = None

def get_db():
    """
    Função geradora para obter sessão de banco de dados.
    
    Yields:
        sqlalchemy.orm.Session: Sessão de banco de dados
    """
    if SessionLocal is None:
        raise RuntimeError("Banco de dados não foi inicializado corretamente")
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Exportar símbolos explicitamente
__all__ = ['Base', 'get_db', 'engine', 'SessionLocal']
