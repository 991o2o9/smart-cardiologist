#!/usr/bin/env python3
"""
Скрипт для применения миграции активного чата
"""

import asyncio
import sys
import os

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from alembic.config import Config
from alembic import command
from services.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

async def check_tables():
    """Проверяем что таблицы обновлены"""
    async for db in get_db():
        try:
            # Проверяем что поле active_chat_id добавлено в users
            result = await db.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'users' AND column_name = 'active_chat_id'
            """))
            if result.fetchone():
                print("✅ Поле active_chat_id добавлено в таблицу users")
            else:
                print("❌ Поле active_chat_id НЕ найдено в таблице users")
            
            # Проверяем что поле is_active добавлено в cardio_chats
            result = await db.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'cardio_chats' AND column_name = 'is_active'
            """))
            if result.fetchone():
                print("✅ Поле is_active добавлено в таблицу cardio_chats")
            else:
                print("❌ Поле is_active НЕ найдено в таблице cardio_chats")
            
            break
        except Exception as e:
            print(f"❌ Ошибка при проверке таблиц: {e}")
            break

def apply_migration():
    """Применить миграцию"""
    print("Применяем миграцию для поддержки активного чата...")
    
    # Создаем конфигурацию Alembic
    alembic_cfg = Config("alembic.ini")
    
    try:
        # Применяем миграцию
        command.upgrade(alembic_cfg, "003")
        print("✅ Миграция успешно применена")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при применении миграции: {e}")
        return False

async def main():
    """Основная функция"""
    success = apply_migration()
    if success:
        await check_tables()
        print("\n🎉 Миграция активного чата успешно завершена!")
        print("\nНовые API эндпоинты:")
        print("- GET /cardio-assistant/active - получить активный чат")
        print("- POST /cardio-assistant/create - создать новый чат")
        print("- POST /cardio-assistant/history/{chat_id}/activate - активировать чат")
    else:
        print("\n❌ Миграция не удалась!")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
