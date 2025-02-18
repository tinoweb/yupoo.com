from sqlalchemy import create_engine
from sqlalchemy import inspect

# URL do banco de dados
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:tinoweb@localhost:5432/yupoo_db"

# Criar engine
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Inspecionar a tabela
inspector = inspect(engine)
table_columns = inspector.get_columns('extractions')

print("Colunas da tabela 'extractions':")
for column in table_columns:
    print(column['name'])
