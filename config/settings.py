import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):    
    DATABASE_URL: Optional[str] = None 
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "mydb"
    DB_USER: str = "myuser"
    DB_PASSWORD: str = "mypassword"
    
    # JWT
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    
    # Email
    MAIL_USERNAME: str = "your-email@gmail.com"
    MAIL_PASSWORD: str = "your-app-password"
    MAIL_FROM: str = "your-email@gmail.com"
    MAIL_PORT: int = 587
    MAIL_SERVER: str = "smtp.gmail.com"
    MAIL_TLS: bool = True
    MAIL_SSL: bool = False
    
    # Активация
    ACTIVATION_CODE_EXPIRE_MINUTES: int = 10
    MAX_ACTIVATION_ATTEMPTS: int = 5
    
    # AI Service
    GROQ_API_KEY: Optional[str] = None
    
    # Rate Limiting
    RATE_LIMIT: int = 5
    CACHE_TTL: int = 300
    
    # CORS Configuration
    ALLOWED_ORIGINS: str = "http://localhost:5173"
    
    # Model Configuration
    MODEL_PATH: str = "data/processed/model.pkl"
    
    # Режим разработки
    DEBUG: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()


def get_database_url() -> str:
    """Получить URL базы данных (Railway или локальный)"""
    if settings.DATABASE_URL:
        url = settings.DATABASE_URL        
        if url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return url
    
    return f"postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
