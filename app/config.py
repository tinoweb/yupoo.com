import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Railway fornece estas variáveis automaticamente
    RAILWAY_ENVIRONMENT: str = os.getenv("RAILWAY_ENVIRONMENT", "development")
    PORT: int = int(os.getenv("PORT", "8000"))
    RAILWAY_PUBLIC_DOMAIN: str = os.getenv("RAILWAY_PUBLIC_DOMAIN", "localhost")
    
    # Configurações da aplicação
    APP_NAME: str = "Yupoo Extractor"
    API_PREFIX: str = "/api/v1"
    DEBUG: bool = RAILWAY_ENVIRONMENT != "production"
    
    class Config:
        case_sensitive = True

settings = Settings()
