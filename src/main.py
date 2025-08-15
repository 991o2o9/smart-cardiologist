import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from config.settings import settings

# Импорт роутеров
from src.api.cardio_assistant import router as cardio_router
from src.api.heart_prediction import router as heart_router
from src.api.auth import router as auth_router
from src.api.analytics import router as analytics_router

# Импорт сервисов
from src.services.database import init_db, close_db, check_db_connection
from src.services.email_service import EmailService

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    # Запуск
    logger.info("Starting Smart Cardiologist API...")
    
    try:
        # Инициализируем базу данных
        await init_db()
        logger.info("Database initialized successfully")
        
        # Проверяем подключение к email серверу
        email_service = EmailService()
        email_connected = await email_service.test_connection()
        if email_connected:
            logger.info("Email service connected successfully")
        else:
            logger.warning("Email service connection failed - check configuration")
        
    except Exception as e:
        logger.error(f"Failed to initialize application: {e}")
        raise
    
    yield
    
    # Завершение
    logger.info("Shutting down Smart Cardiologist API...")
    await close_db()
    logger.info("Application shutdown complete")


# Создаем FastAPI приложение
app = FastAPI(
    title="Smart Cardiologist API",
    description="Интеллектуальный помощник кардиолога с использованием AI и ML",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Настройки CORS
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роутеры
app.include_router(auth_router, prefix="/api/v1")
app.include_router(cardio_router, prefix="/api/v1")
app.include_router(heart_router, prefix="/api/v1")
app.include_router(analytics_router, prefix="/api/v1")


@app.get("/")
async def root():
    """Корневой endpoint"""
    return {
        "message": "Smart Cardiologist API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "auth": {
                "register": "/api/v1/auth/register",
                "login": "/api/v1/auth/login",
                "activate": "/api/v1/auth/activate",
                "me": "/api/v1/auth/me"
            },
            "cardio_assistant": {
                "analysis": "/api/v1/cardio-assistant/",
                "history": "/api/v1/cardio-assistant/history"
            },
            "heart_prediction": "/api/v1/heart-prediction/predict"
        }
    }


@app.get("/health")
async def health_check():
    """Общая проверка здоровья приложения"""
    try:        
        db_healthy = await check_db_connection()
        
        return {
            "status": "healthy" if db_healthy else "degraded",
            "service": "Smart Cardiologist API",
            "version": "1.0.0",
            "database": "connected" if db_healthy else "disconnected",
            "timestamp": "2024-01-01T00:00:00Z"  
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail="Health check failed")


@app.get("/config")
async def get_config():
    """Получить конфигурацию приложения (только для разработки)"""
    if settings.DEBUG:
        return {
            "database": {
                "host": settings.DB_HOST,
                "port": settings.DB_PORT,
                "name": settings.DB_NAME,
                "user": settings.DB_USER
            },
            "email": {
                "server": settings.MAIL_SERVER,
                "port": settings.MAIL_PORT,
                "username": settings.MAIL_USERNAME
            },
            "jwt": {
                "algorithm": settings.ALGORITHM,
                "expire_minutes": settings.ACCESS_TOKEN_EXPIRE_MINUTES
            }
        }
    else:
        raise HTTPException(status_code=404, detail="Not found")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        log_level="info"
    )
