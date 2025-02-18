from sqlalchemy import create_engine, MetaData, Table, Column, DateTime, String, text
from sqlalchemy.ext.declarative import declarative_base

# Configuração do banco de dados
SQLALCHEMY_DATABASE_URL = "sqlite:///./yupoo_extractor.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
metadata = MetaData()

def upgrade():
    # Conectar ao banco de dados
    connection = engine.connect()
    transaction = connection.begin()

    try:
        # Adicionar novas colunas à tabela extractions
        connection.execute(text("""
            ALTER TABLE extractions 
            ADD COLUMN started_at TIMESTAMP;
        """))
        
        connection.execute(text("""
            ALTER TABLE extractions 
            ADD COLUMN error_message TEXT;
        """))

        transaction.commit()
        print("Migração concluída com sucesso!")
        
    except Exception as e:
        transaction.rollback()
        print(f"Erro durante a migração: {str(e)}")
        raise
    finally:
        connection.close()

if __name__ == "__main__":
    upgrade()
