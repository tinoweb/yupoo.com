from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    email: str
    username: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class ExtractionBase(BaseModel):
    url: str

class ExtractionCreate(ExtractionBase):
    pass

class Extraction(ExtractionBase):
    id: int
    status: str
    created_at: datetime
    completed_at: Optional[datetime]
    result_path: Optional[str]
    user_id: int

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
