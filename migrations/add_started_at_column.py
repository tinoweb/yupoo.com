from sqlalchemy import create_engine, text

# URL do banco de dados
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:tinoweb@localhost:5432/yupoo_db"

# Criar engine
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Executar a migração
with engine.connect() as conn:
    conn.execute(text("ALTER TABLE extractions ADD COLUMN started_at TIMESTAMP;"))
    conn.commit()

print("Coluna 'started_at' adicionada com sucesso!")
