#!/usr/bin/env python3
"""
Скрипт для настройки базы данных PostgreSQL
"""
import asyncio
import asyncpg
import logging
import sys
import os

# Добавляем корневую директорию проекта в путь
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def setup_database():
    """Настройка базы данных PostgreSQL"""
    try:
        # Подключаемся к PostgreSQL как суперпользователь
        # Обычно это postgres пользователь
        conn = await asyncpg.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            user='postgres',  # Суперпользователь
            password='',  # Пароль суперпользователя (если есть)
            database='postgres'  # Системная база данных
        )
        
        logger.info("Connected to PostgreSQL as superuser")
        
        # Создаем пользователя
        try:
            await conn.execute(f"""
                CREATE USER {settings.DB_USER} 
                WITH PASSWORD '{settings.DB_PASSWORD}'
            """)
            logger.info(f"User {settings.DB_USER} created successfully")
        except asyncpg.exceptions.DuplicateObjectError:
            logger.info(f"User {settings.DB_USER} already exists")
        
        # Создаем базу данных
        try:
            await conn.execute(f"""
                CREATE DATABASE {settings.DB_NAME}
                OWNER {settings.DB_USER}
            """)
            logger.info(f"Database {settings.DB_NAME} created successfully")
        except asyncpg.exceptions.DuplicateDatabaseError:
            logger.info(f"Database {settings.DB_NAME} already exists")
        
        # Предоставляем права пользователю
        await conn.execute(f"""
            GRANT ALL PRIVILEGES ON DATABASE {settings.DB_NAME} TO {settings.DB_USER}
        """)
        
        # Подключаемся к созданной базе данных для настройки схемы
        await conn.close()
        
        conn = await asyncpg.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            database=settings.DB_NAME
        )
        
        logger.info(f"Connected to database {settings.DB_NAME} as {settings.DB_USER}")
        
        # Создаем расширения если нужно
        try:
            await conn.execute("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\"")
            logger.info("UUID extension created/enabled")
        except Exception as e:
            logger.warning(f"Could not create UUID extension: {e}")
        
        await conn.close()
        logger.info("Database setup completed successfully")
        
    except Exception as e:
        logger.error(f"Database setup failed: {e}")
        raise


async def test_connection():
    """Тестирование подключения к базе данных"""
    try:
        conn = await asyncpg.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            database=settings.DB_NAME
        )
        
        # Выполняем простой запрос
        result = await conn.fetchval("SELECT 1")
        logger.info(f"Connection test successful: {result}")
        
        await conn.close()
        return True
        
    except Exception as e:
        logger.error(f"Connection test failed: {e}")
        return False


async def main():
    """Основная функция"""
    logger.info("Starting database setup...")
    
    try:
        await setup_database()
        await test_connection()
        logger.info("Database setup completed successfully!")
        
    except Exception as e:
        logger.error(f"Database setup failed: {e}")
        exit(1)


if __name__ == "__main__":
    asyncio.run(main())
