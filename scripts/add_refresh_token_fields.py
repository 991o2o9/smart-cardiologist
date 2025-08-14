#!/usr/bin/env python3
"""
Скрипт для добавления полей refresh token в таблицу users
"""

import asyncio
import asyncpg
import sys
import os

# Добавляем корневую директорию проекта в путь
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import settings

async def add_refresh_token_fields():
    """Добавление полей refresh token в таблицу users"""
    try:
        # Сначала подключаемся как суперпользователь
        conn = await asyncpg.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            user='postgres',  # Суперпользователь
            password='',  # Пароль суперпользователя (если есть)
            database=settings.DB_NAME
        )
        
        print("🔧 Добавляем поля refresh token в таблицу users...")
        
        # Проверяем, есть ли уже поля
        columns = await conn.fetch("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'users' AND column_name IN ('refresh_token', 'refresh_token_expires')
        """)
        
        existing_columns = [col['column_name'] for col in columns]
        print(f"Существующие поля refresh token: {existing_columns}")
        
        # Добавляем поле refresh_token если его нет
        if 'refresh_token' not in existing_columns:
            await conn.execute("""
                ALTER TABLE users 
                ADD COLUMN refresh_token VARCHAR(500)
            """)
            print("✅ Добавлено поле refresh_token")
        else:
            print("ℹ️  Поле refresh_token уже существует")
        
        # Добавляем поле refresh_token_expires если его нет
        if 'refresh_token_expires' not in existing_columns:
            await conn.execute("""
                ALTER TABLE users 
                ADD COLUMN refresh_token_expires TIMESTAMP
            """)
            print("✅ Добавлено поле refresh_token_expires")
        else:
            print("ℹ️  Поле refresh_token_expires уже существует")
        
        # Проверяем результат
        columns = await conn.fetch("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_name = 'users' AND column_name IN ('refresh_token', 'refresh_token_expires')
            ORDER BY column_name
        """)
        
        print("\n📋 Обновленная структура таблицы users:")
        for col in columns:
            nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
            print(f"  - {col['column_name']}: {col['data_type']} ({nullable})")
        
        await conn.close()
        print("\n✅ Поля refresh token успешно добавлены!")
        
    except Exception as e:
        print(f"❌ Ошибка при добавлении полей: {e}")

if __name__ == "__main__":
    asyncio.run(add_refresh_token_fields())
