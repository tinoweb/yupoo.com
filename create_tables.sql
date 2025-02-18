-- Criar tabela de usuários
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(100) UNIQUE,
    username VARCHAR(50) UNIQUE,
    hashed_password VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP
);

-- Criar tabela de extrações
CREATE TABLE IF NOT EXISTS extractions (
    id SERIAL PRIMARY KEY,
    url VARCHAR(500),
    status VARCHAR(20),
    created_at TIMESTAMP,
    completed_at TIMESTAMP,
    result_path VARCHAR(500),
    user_id INTEGER REFERENCES users(id)
);
