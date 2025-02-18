from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, index=True)
    username = Column(String(50), unique=True, index=True)
    hashed_password = Column(String(100))
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)  # Novo campo para indicar se é administrador
    created_at = Column(DateTime, default=datetime.utcnow)
    extractions = relationship("Extraction", back_populates="user")

class Extraction(Base):
    __tablename__ = "extractions"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Tornando opcional
    status = Column(String)  # pending, processing, completed, failed
    created_at = Column(DateTime)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(String, nullable=True)
    result_path = Column(String, nullable=True)

    user = relationship("User", back_populates="extractions")
