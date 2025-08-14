#!/usr/bin/env python3
"""
Скрипт для проверки пользователя в базе данных
"""

import asyncio
import asyncpg
import sys
import os

# Добавляем корневую директорию проекта в путь
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import settings

async def check_user(email: str):
    """Проверка пользователя в базе данных"""
    try:
        conn = await asyncpg.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            database=settings.DB_NAME
        )
        
        print(f"🔍 Проверяем пользователя: {email}")
        
        # Получаем информацию о пользователе
        user = await conn.fetchrow("""
            SELECT id, email, is_activated, activation_code, activation_code_expires, 
                   refresh_token, refresh_token_expires, created_at
            FROM users 
            WHERE email = $1
        """, email)
        
        if user:
            print(f"✅ Пользователь найден:")
            print(f"  - ID: {user['id']}")
            print(f"  - Email: {user['email']}")
            print(f"  - Активирован: {user['is_activated']}")
            print(f"  - Код активации: {user['activation_code']}")
            print(f"  - Код истекает: {user['activation_code_expires']}")
            print(f"  - Refresh token: {'Есть' if user['refresh_token'] else 'Нет'}")
            print(f"  - Refresh token истекает: {user['refresh_token_expires']}")
            print(f"  - Создан: {user['created_at']}")
        else:
            print(f"❌ Пользователь не найден")
        
        await conn.close()
        
    except Exception as e:
        print(f"❌ Ошибка при проверке пользователя: {e}")

if __name__ == "__main__":
    email = "test4@example.com"
    asyncio.run(check_user(email))
