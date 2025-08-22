import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):    
    DATABASE_URL: str
    
    # JWT
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30 
    
    # Email
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_TLS: bool
    MAIL_SSL: bool
    
    # Активация
    ACTIVATION_CODE_EXPIRE_MINUTES: int
    MAX_ACTIVATION_ATTEMPTS: int
    
    # AI Service
    GROQ_API_KEY: Optional[str] = None
    
    # Rate Limiting
    RATE_LIMIT: int
    CACHE_TTL: int
    
    # CORS Configuration
    ALLOWED_ORIGINS: str
    
    # Model Configuration
    MODEL_PATH: str
    
    # Режим разработки
    DEBUG: bool
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
