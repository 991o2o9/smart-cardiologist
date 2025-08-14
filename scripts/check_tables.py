#!/usr/bin/env python3
"""
Скрипт для проверки таблиц в базе данных
"""

import asyncio
import asyncpg
import sys
import os

# Добавляем корневую директорию проекта в путь
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import settings

async def check_tables():
    """Проверка таблиц в базе данных"""
    try:
        conn = await asyncpg.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            database=settings.DB_NAME
        )
        
        print("🔍 Проверяем таблицы в базе данных...")
        
        # Получаем список всех таблиц
        tables = await conn.fetch("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        
        print(f"📋 Найдено таблиц: {len(tables)}")
        
        for table in tables:
            table_name = table['table_name']
            print(f"  - {table_name}")
            
            # Проверяем структуру таблицы
            columns = await conn.fetch(f"""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_name = '{table_name}'
                ORDER BY ordinal_position
            """)
            
            print(f"    Колонки:")
            for col in columns:
                nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
                print(f"      - {col['column_name']}: {col['data_type']} ({nullable})")
            
            # Проверяем количество записей
            count = await conn.fetchval(f"SELECT COUNT(*) FROM {table_name}")
            print(f"    Записей: {count}")
            print()
        
        await conn.close()
        
    except Exception as e:
        print(f"❌ Ошибка при проверке таблиц: {e}")

if __name__ == "__main__":
    asyncio.run(check_tables())
