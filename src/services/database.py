from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from config.settings import get_database_url
from models.database import Base
import logging

logger = logging.getLogger(__name__)

# Создаем асинхронный движок
engine = create_async_engine(
    get_database_url(),
    echo=False,  # Установите True для отладки SQL запросов
    pool_pre_ping=True,
    pool_recycle=300,
)

# Создаем фабрику сессий
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def get_db() -> AsyncSession:
    """Получить сессию базы данных"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"Database error: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """Инициализировать базу данных"""
    try:
        async with engine.begin() as conn:
            # Проверяем подключение
            result = await conn.execute(text("SELECT 1"))
            logger.info("Database connection test successful")
            
            # Проверяем, существуют ли таблицы
            try:
                result = await conn.execute(text("SELECT COUNT(*) FROM users"))
                logger.info("Database tables already exist, skipping creation")
            except Exception:
                # Создаем все таблицы только если их нет
                await conn.run_sync(Base.metadata.create_all)
                logger.info("Database tables created successfully")
            
    except Exception as e:
        logger.error(f"Database initialization error: {e}")
        raise


async def close_db():
    """Закрыть соединения с базой данных"""
    await engine.dispose()
    logger.info("Database connections closed")


async def check_db_connection():
    """Проверить подключение к базе данных"""
    try:
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT 1"))
            return True
    except Exception as e:
        logger.error(f"Database connection check failed: {e}")
        return False
