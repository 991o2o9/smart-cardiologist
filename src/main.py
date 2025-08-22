import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from config.settings import settings

# Import routers
from api.cardio_assistant import router as cardio_router
from api.heart_prediction import router as heart_router
from api.auth import router as auth_router
from api.analytics import router as analytics_router

# Import services
from services.database import init_db, close_db, check_db_connection, engine
from services.email_service import EmailService

# Import models
from models import Base

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management"""
    logger.info("Starting Smart Cardiologist API...")

    try:
        # Initialize database
        await init_db()

        # Создаём таблицы, если их нет
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database initialized and tables ensured")

        # Check email server connection
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

    logger.info("Shutting down Smart Cardiologist API...")
    await close_db()
    logger.info("Application shutdown complete")


# Create FastAPI application
app = FastAPI(
    title="Smart Cardiologist API",
    description="AI-powered cardiology assistant for heart disease risk prediction and health analysis",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(heart_router)
app.include_router(cardio_router)
app.include_router(analytics_router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Smart Cardiologist API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
async def health_check():
    """General application health check"""
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
    """
    Get application configuration (without sensitive data)
    """
    return {
        "debug": settings.DEBUG,
        "database_host": settings.DB_HOST,
        "database_port": settings.DB_PORT,
        "database_name": settings.DB_NAME,
        "rate_limit": settings.RATE_LIMIT,
        "cache_ttl": settings.CACHE_TTL,
        "allowed_origins": settings.ALLOWED_ORIGINS.split(",")
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
