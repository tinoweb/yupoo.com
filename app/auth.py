from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from . import models, schemas
from .database import get_db
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password, hashed_password):
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        print(f"Erro ao verificar senha: {str(e)}")
        return False

def get_password_hash(password):
    try:
        return pwd_context.hash(password)
    except Exception as e:
        print(f"Erro ao gerar hash da senha: {str(e)}")
        raise

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    try:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    except Exception as e:
        print(f"Erro ao criar token de acesso: {str(e)}")
        raise

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Se o token começar com "Bearer ", remova-o
        if token.startswith("Bearer "):
            token = token.replace("Bearer ", "")
            
        print(f"Decodificando token: {token}")  # Debug log
        
        # Verificar se o token está vazio ou é inválido
        if not token or token.isspace():
            print("Token vazio ou inválido")
            raise credentials_exception
            
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            print("Token não contém username")  # Debug log
            raise credentials_exception
            
        print(f"Username do token: {username}")  # Debug log
        token_data = schemas.TokenData(username=username)
        
        # Verificar se o token expirou
        exp = payload.get("exp")
        if exp is None:
            print("Token não contém data de expiração")
            raise credentials_exception
            
        # Verificar se o token já expirou
        if datetime.utcfromtimestamp(exp) < datetime.utcnow():
            print("Token expirado")
            raise credentials_exception
            
    except JWTError as e:
        print(f"Erro ao decodificar token: {str(e)}")  # Debug log
        raise credentials_exception
    except Exception as e:
        print(f"Erro inesperado ao validar usuário: {str(e)}")  # Debug log
        raise credentials_exception

    user = db.query(models.User).filter(models.User.username == token_data.username).first()
    if user is None:
        print(f"Usuário não encontrado: {username}")  # Debug log
        raise credentials_exception
        
    print(f"Usuário autenticado: {user.username}")  # Debug log
    return user
