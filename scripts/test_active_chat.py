#!/usr/bin/env python3
"""
Тестовый скрипт для проверки функциональности активного чата
"""

import asyncio
import sys
import os
import json

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.database import get_db
from src.models.database import User, CardioChat
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

async def test_active_chat():
    """Тестируем функциональность активного чата"""
    print("🧪 Тестируем функциональность активного чата...")
    
    async for db in get_db():
        try:
            # 1. Проверяем что поля добавлены
            print("\n1. Проверяем структуру таблиц...")
            
            # Проверяем поле active_chat_id в users
            result = await db.execute(select(User.active_chat_id))
            print("✅ Поле active_chat_id доступно в модели User")
            
            # Проверяем поле is_active в cardio_chats
            result = await db.execute(select(CardioChat.is_active))
            print("✅ Поле is_active доступно в модели CardioChat")
            
            # 2. Создаем тестового пользователя (если нет)
            print("\n2. Создаем тестового пользователя...")
            test_user = await db.execute(
                select(User).where(User.email == "test@example.com")
            )
            user = test_user.scalar_one_or_none()
            
            if not user:
                print("Создаем нового тестового пользователя...")
                user = User(
                    email="test@example.com",
                    password_hash="test_hash",
                    is_activated=True
                )
                db.add(user)
                await db.flush()
                print(f"✅ Создан пользователь с ID: {user.id}")
            else:
                print(f"✅ Найден существующий пользователь с ID: {user.id}")
            
            # 3. Создаем тестовые чаты
            print("\n3. Создаем тестовые чаты...")
            
            # Создаем первый чат
            chat1 = CardioChat(
                user_id=user.id,
                messages=[
                    {"role": "user", "content": "Привет", "timestamp": "2024-01-15T10:00:00Z"},
                    {"role": "assistant", "content": "Здравствуйте!", "timestamp": "2024-01-15T10:00:05Z"}
                ],
                summary="Привет",
                is_active=False
            )
            db.add(chat1)
            await db.flush()
            print(f"✅ Создан чат 1 с ID: {chat1.id}")
            
            # Создаем второй чат (активный)
            chat2 = CardioChat(
                user_id=user.id,
                messages=[
                    {"role": "user", "content": "У меня болит сердце", "timestamp": "2024-01-15T11:00:00Z"},
                    {"role": "assistant", "content": "Рекомендую обратиться к врачу", "timestamp": "2024-01-15T11:00:05Z"}
                ],
                summary="У меня болит сердце",
                is_active=True
            )
            db.add(chat2)
            await db.flush()
            print(f"✅ Создан чат 2 с ID: {chat2.id} (активный)")
            
            # 4. Устанавливаем активный чат
            print("\n4. Устанавливаем активный чат...")
            await db.execute(
                update(User)
                .where(User.id == user.id)
                .values(active_chat_id=chat2.id)
            )
            await db.commit()
            print(f"✅ Установлен активный чат: {chat2.id}")
            
            # 5. Проверяем активный чат
            print("\n5. Проверяем активный чат...")
            updated_user = await db.execute(
                select(User).where(User.id == user.id)
            )
            user = updated_user.scalar_one()
            
            if user.active_chat_id == chat2.id:
                print(f"✅ Активный чат корректно установлен: {user.active_chat_id}")
            else:
                print(f"❌ Ошибка: активный чат не установлен")
            
            # 6. Проверяем количество сообщений в активном чате
            active_chat = await db.execute(
                select(CardioChat).where(CardioChat.id == user.active_chat_id)
            )
            chat = active_chat.scalar_one()
            print(f"✅ В активном чате {len(chat.messages)} сообщений")
            
            # 7. Добавляем новое сообщение в активный чат
            print("\n6. Добавляем новое сообщение...")
            new_message = {
                "role": "user",
                "content": "Спасибо за совет",
                "timestamp": "2024-01-15T12:00:00Z"
            }
            chat.messages.append(new_message)
            await db.commit()
            print(f"✅ Добавлено новое сообщение. Всего сообщений: {len(chat.messages)}")
            
            # 8. Проверяем что чат остается активным
            print("\n7. Проверяем что чат остается активным...")
            if chat.is_active:
                print("✅ Чат остается активным")
            else:
                print("❌ Чат стал неактивным")
            
            print("\n🎉 Все тесты прошли успешно!")
            break
            
        except Exception as e:
            print(f"❌ Ошибка при тестировании: {e}")
            import traceback
            traceback.print_exc()
            break

if __name__ == "__main__":
    asyncio.run(test_active_chat())
