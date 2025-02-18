import sys
import codecs
import psycopg2
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import psycopg2
import psycopg2.extensions
import logging
from .config import settings
import time
from sqlalchemy.exc import SQLAlchemyError, OperationalError

# Configurar logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configurar encoding para Windows
if sys.platform.startswith('win'):
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
    sys.stdin = codecs.getreader('utf-8')(sys.stdin.buffer)

# Forçar psycopg2 a usar unicode
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)
psycopg2.extensions.register_type(psycopg2.extensions.UNICODEARRAY)

def get_database_url():
    """
    Obtém a URL do banco de dados com tratamento de erros.
    
    Returns:
        str: URL de conexão com o banco de dados
    """
    try:
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
    Base = declarative_base()
    
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

    def create_tables():
        # Primeiro testa a conexão usando psycopg2
        try:
            conn = psycopg2.connect(
                dbname=settings.POSTGRES_DB,
                user=settings.POSTGRES_USER,
                password=settings.POSTGRES_PASSWORD,
                host=settings.POSTGRES_HOST,
                port=settings.POSTGRES_PORT
            )
            conn.set_client_encoding('UTF8')
            cur = conn.cursor()
            cur.execute('SELECT 1')
            cur.close()
            conn.close()
            logger.info("Conexão PostgreSQL testada com sucesso!")
            
            # Se a conexão funcionar, cria as tabelas
            Base.metadata.create_all(bind=engine)
            logger.info("Tabelas criadas com sucesso!")
        except Exception as e:
            logger.error(f"Erro ao conectar/criar tabelas: {e}")
            raise
except Exception as e:
    logger.error(f"Erro crítico ao configurar banco de dados: {e}")
    SessionLocal = None
    engine = None
