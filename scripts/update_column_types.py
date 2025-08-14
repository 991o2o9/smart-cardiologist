#!/usr/bin/env python3
"""
Скрипт для изменения типов полей в базе данных для поддержки шифрования
"""

import asyncio
import asyncpg
import sys
import os

# Добавляем корневую директорию проекта в путь
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import settings

async def update_column_types():
    """Изменение типов полей для поддержки шифрования"""
    try:
        # Подключаемся как суперпользователь
        conn = await asyncpg.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            user='postgres',  # Суперпользователь
            password='',  # Пароль суперпользователя (если есть)
            database=settings.DB_NAME
        )
        
        print("🔧 Обновляем типы полей для поддержки шифрования...")
        
        # Обновляем поля в таблице cardio_analyses
        print("📋 Обновляем таблицу cardio_analyses...")
        
        try:
            await conn.execute("ALTER TABLE cardio_analyses ALTER COLUMN age TYPE TEXT")
            print("✅ age -> TEXT")
        except Exception as e:
            print(f"ℹ️  age уже TEXT или ошибка: {e}")
        
        try:
            await conn.execute("ALTER TABLE cardio_analyses ALTER COLUMN pulse TYPE TEXT")
            print("✅ pulse -> TEXT")
        except Exception as e:
            print(f"ℹ️  pulse уже TEXT или ошибка: {e}")
        
        try:
            await conn.execute("ALTER TABLE cardio_analyses ALTER COLUMN risk TYPE TEXT")
            print("✅ risk -> TEXT")
        except Exception as e:
            print(f"ℹ️  risk уже TEXT или ошибка: {e}")
        
        # Обновляем поля в таблице heart_predictions
        print("📋 Обновляем таблицу heart_predictions...")
        
        columns_to_update = [
            'age', 'sex', 'cp', 'trestbps', 'chol', 'fbs', 'restecg',
            'thalach', 'exang', 'oldpeak', 'slope', 'ca', 'thal', 'pulse',
            'risk_prediction', 'probability'
        ]
        
        for column in columns_to_update:
            try:
                await conn.execute(f"ALTER TABLE heart_predictions ALTER COLUMN {column} TYPE TEXT")
                print(f"✅ {column} -> TEXT")
            except Exception as e:
                print(f"ℹ️  {column} уже TEXT или ошибка: {e}")
        
        await conn.close()
        print("\n✅ Типы полей успешно обновлены!")
        
    except Exception as e:
        print(f"❌ Ошибка при обновлении типов полей: {e}")

if __name__ == "__main__":
    asyncio.run(update_column_types())
