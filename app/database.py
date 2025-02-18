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

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurar encoding para Windows
if sys.platform.startswith('win'):
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
    sys.stdin = codecs.getreader('utf-8')(sys.stdin.buffer)

# Forçar psycopg2 a usar unicode
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)
psycopg2.extensions.register_type(psycopg2.extensions.UNICODEARRAY)

try:
    logger.info(f"Tentando conectar ao banco de dados: {settings.SQLALCHEMY_DATABASE_URL}")

    # Criar engine com configurações do settings
    engine = create_engine(
        settings.SQLALCHEMY_DATABASE_URL,
        pool_pre_ping=True,
        pool_size=settings.SQLALCHEMY_POOL_SIZE,
        max_overflow=settings.SQLALCHEMY_MAX_OVERFLOW,
        echo=settings.SQLALCHEMY_ECHO
    )
    logger.info("Engine criada com sucesso")

    # Configurar sessão
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()

    def get_db():
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
    logger.error(f"Erro ao conectar ao banco de dados: {e}")
    raise
