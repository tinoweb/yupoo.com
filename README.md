# Yupoo Extractor Service

Serviço web para extração de imagens e informações do Yupoo.com

## Requisitos

- Python 3.8+
- Chrome/Chromium (para Selenium)

## Instalação

1. Instale as dependências:
```bash
pip install -r requirements.txt
```

2. Execute o servidor:
```bash
uvicorn app.main:app --reload
```

O banco de dados SQLite será criado automaticamente na primeira execução.

## Endpoints da API

- POST /token - Login (obter token JWT)
- POST /users/ - Criar novo usuário
- POST /extractions/ - Criar nova extração
- GET /extractions/ - Listar extrações do usuário

## Uso

1. Crie um usuário via POST /users/
2. Faça login via POST /token para obter o token JWT
3. Use o token nas requisições para /extractions/

## Plano Gratuito (MVP)

- 100 extrações por dia
- Armazenamento de imagens por 7 dias
- Exportação em JSON e CSV
