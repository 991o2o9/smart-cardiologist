#!/usr/bin/env python3
"""
Тест для проверки исправления refresh token
"""

import asyncio
import aiohttp
import json
from typing import Dict, Any


class RefreshTokenTest:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = None
        self.access_token = None
        self.refresh_token = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def test_login(self) -> bool:
        """Тест входа в систему"""
        print("🔐 Тестирую вход в систему...")
        
        login_data = {
            "email": "test@example.com",
            "password": "testpassword123"
        }
        
        try:
            async with self.session.post(
                f"{self.base_url}/auth/login",
                json=login_data
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    self.access_token = data["access_token"]
                    self.refresh_token = data["refresh_token"]
                    print("✅ Вход успешен")
                    print(f"   Access Token: {self.access_token[:50]}...")
                    print(f"   Refresh Token: {self.refresh_token[:50]}...")
                    return True
                else:
                    print(f"❌ Ошибка входа: {response.status}")
                    error_data = await response.json()
                    print(f"   Детали: {error_data}")
                    return False
        except Exception as e:
            print(f"❌ Ошибка при входе: {e}")
            return False
    
    async def test_refresh_token(self) -> bool:
        """Тест обновления токена"""
        print("\n🔄 Тестирую обновление токена...")
        
        if not self.refresh_token:
            print("❌ Нет refresh token для тестирования")
            return False
        
        refresh_data = {
            "refresh_token": self.refresh_token
        }
        
        try:
            async with self.session.post(
                f"{self.base_url}/auth/refresh",
                json=refresh_data
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print("✅ Обновление токена успешно")
                    print(f"   Новый Access Token: {data['access_token'][:50]}...")
                    print(f"   Новый Refresh Token: {data['refresh_token'][:50]}...")
                    print(f"   Expires In: {data['expires_in']} минут")
                    print(f"   Refresh Expires In: {data['refresh_expires_in']} дней")
                    
                    # Обновляем токены для дальнейшего использования
                    self.access_token = data["access_token"]
                    self.refresh_token = data["refresh_token"]
                    return True
                else:
                    print(f"❌ Ошибка обновления токена: {response.status}")
                    error_data = await response.json()
                    print(f"   Детали: {error_data}")
                    return False
        except Exception as e:
            print(f"❌ Ошибка при обновлении токена: {e}")
            return False
    
    async def test_logout(self) -> bool:
        """Тест выхода из системы"""
        print("\n🚪 Тестирую выход из системы...")
        
        if not self.access_token:
            print("❌ Нет access token для выхода")
            return False
        
        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }
        
        try:
            async with self.session.post(
                f"{self.base_url}/auth/logout",
                headers=headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print("✅ Выход успешен")
                    print(f"   Сообщение: {data['message']}")
                    return True
                else:
                    print(f"❌ Ошибка выхода: {response.status}")
                    error_data = await response.json()
                    print(f"   Детали: {error_data}")
                    return False
        except Exception as e:
            print(f"❌ Ошибка при выходе: {e}")
            return False
    
    async def run_tests(self):
        """Запуск всех тестов"""
        print("🧪 Запуск тестов refresh token...")
        print(f"📍 URL: {self.base_url}")
        print("=" * 50)
        
        # Тест 1: Вход
        if not await self.test_login():
            print("\n❌ Тест входа не прошел, останавливаюсь")
            return
        
        # Тест 2: Обновление токена
        if not await self.test_refresh_token():
            print("\n❌ Тест обновления токена не прошел")
            return
        
        # Тест 3: Выход
        if not await self.test_logout():
            print("\n❌ Тест выхода не прошел")
            return
        
        print("\n" + "=" * 50)
        print("🎉 Все тесты прошли успешно!")
        print("✅ Проблема с refresh token исправлена")


async def main():
    """Главная функция"""
    # URL вашего API
    base_url = "http://localhost:8000"  # Измените на ваш URL
    
    print("🚀 Запуск теста исправления refresh token")
    print("⚠️  Убедитесь, что сервер запущен и доступен")
    print("⚠️  Убедитесь, что в базе данных есть тестовый пользователь")
    print("⚠️  Измените base_url в скрипте, если необходимо")
    print()
    
    async with RefreshTokenTest(base_url) as tester:
        await tester.run_tests()


if __name__ == "__main__":
    asyncio.run(main())
