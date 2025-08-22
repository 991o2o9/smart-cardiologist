import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from config.settings import settings

# Import routers
from src.api.cardio_assistant import router as cardio_router
from src.api.heart_prediction import router as heart_router
from src.api.auth import router as auth_router
from src.api.analytics import router as analytics_router

# Import services
from src.services.database import init_db, close_db, check_db_connection
from src.services.email_service import EmailService
from src.services.ai_service import AIService

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management"""
    # Startup
    logger.info("Starting Smart Cardiologist API...")
    
    try:
        # Initialize database
        await init_db()
        logger.info("Database initialized successfully")
        
        # Check email server connection
        email_service = EmailService()
        email_connected = await email_service.test_connection()
        if email_connected:
            logger.info("Email service connected successfully")
        else:
            logger.warning("Email service connection failed - check configuration")
        
        # Initialize AI service and log provider
        try:
            ai_service = AIService()
            provider_info = ai_service.get_provider_info()
            logger.info(f"AI Service initialized successfully - Provider: {provider_info['provider']}, Model: {provider_info['model']}")
        except Exception as e:
            logger.error(f"AI Service initialization failed: {e}")
            # Don't raise here as AI service is not critical for startup
        
    except Exception as e:
        logger.error(f"Failed to initialize application: {e}")
        raise
    
    yield
    
    # Shutdown
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
def get_cors_origins():
    """Get CORS origins based on environment"""
    # If ALLOWED_ORIGINS is empty or not set, allow all origins
    if not settings.ALLOWED_ORIGINS or settings.ALLOWED_ORIGINS.strip() == "":
        logger.info("CORS: All origins allowed (ALLOWED_ORIGINS not set)")
        return ["*"]
    
    origins = settings.ALLOWED_ORIGINS.split(",")
    
    # Add development origins if in debug mode
    if settings.DEBUG:
        dev_origins = [
            "http://localhost:3000",
            "http://localhost:5173", 
            "http://127.0.0.1:3000",
            "http://127.0.0.1:5173"
        ]
        origins.extend(dev_origins)
    
    # Remove duplicates and empty strings
    origins = list(set(filter(None, origins)))
    
    logger.info(f"CORS origins configured: {origins}")
    return origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=settings.ALLOW_CREDENTIALS,
    allow_methods=settings.ALLOWED_METHODS.split(","),
    allow_headers=settings.ALLOWED_HEADERS.split(",") if settings.ALLOWED_HEADERS != "*" else ["*"],
    max_age=settings.MAX_AGE,
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
        
        # Check AI service health
        ai_healthy = False
        ai_provider = "unknown"
        try:
            ai_service = AIService()
            provider_info = ai_service.get_provider_info()
            ai_healthy = provider_info['healthy']
            ai_provider = provider_info['provider']
        except Exception as e:
            logger.error(f"AI service health check failed: {e}")
        
        overall_status = "healthy" if db_healthy and ai_healthy else "degraded"
        
        return {
            "status": overall_status,
            "service": "Smart Cardiologist API",
            "version": "1.0.0",
            "database": "connected" if db_healthy else "disconnected",
            "ai_service": {
                "provider": ai_provider,
                "status": "connected" if ai_healthy else "disconnected"
            },
            "timestamp": "2024-01-01T00:00:00Z"  
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail="Health check failed")


@app.get("/config")
async def get_config():
    """
    Get application configuration (without sensitive data)
    
    Returns basic configuration information
    """
    # Get AI provider info
    ai_provider = "unknown"
    ai_model = "unknown"
    try:
        ai_service = AIService()
        provider_info = ai_service.get_provider_info()
        ai_provider = provider_info['provider']
        ai_model = provider_info['model']
    except Exception as e:
        logger.error(f"Failed to get AI provider info: {e}")
    
    return {
        "debug": settings.DEBUG,
        "database_host": settings.DB_HOST,
        "database_port": settings.DB_PORT,
        "database_name": settings.DB_NAME,
        "rate_limit": settings.RATE_LIMIT,
        "cache_ttl": settings.CACHE_TTL,
        "ai_provider": ai_provider,
        "ai_model": ai_model,
        "allowed_origins": get_cors_origins(),
        "cors_all_origins_allowed": "*" in get_cors_origins(),
        "cors_methods": settings.ALLOWED_METHODS.split(","),
        "cors_headers": settings.ALLOWED_HEADERS.split(",") if settings.ALLOWED_HEADERS != "*" else ["*"],
        "cors_credentials": settings.ALLOW_CREDENTIALS,
        "cors_max_age": settings.MAX_AGE
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        log_level="info"
    )
