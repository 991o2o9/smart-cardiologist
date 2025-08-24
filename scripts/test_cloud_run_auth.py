#!/usr/bin/env python3
"""
Тест аутентификации для Cloud Run
Проверяет работу refresh token и сессий
"""

import asyncio
import aiohttp
import json
import time
from typing import Dict, Any, Optional


class CloudRunAuthTester:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = None
        self.access_token = None
        self.refresh_token = None
        self.user_email = "test@example.com"
        self.user_password = "testpassword123"

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def test_register(self) -> bool:
        """Тест регистрации пользователя"""
        print("📝 Тестирую регистрацию...")
        
        register_data = {
            "email": self.user_email,
            "password": self.user_password
        }
        
        try:
            async with self.session.post(
                f"{self.base_url}/auth/register",
                json=register_data
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print("✅ Регистрация успешна")
                    print(f"   Сообщение: {data.get('message', 'N/A')}")
                    return True
                elif response.status == 400:
                    data = await response.json()
                    if "already exists" in data.get('detail', ''):
                        print("ℹ️  Пользователь уже существует, продолжаем...")
                        return True
                    else:
                        print(f"❌ Ошибка регистрации: {data}")
                        return False
                else:
                    print(f"❌ Ошибка регистрации: {response.status}")
                    return False
        except Exception as e:
            print(f"❌ Ошибка при регистрации: {e}")
            return False

    async def test_login(self) -> bool:
        """Тест входа в систему"""
        print("\n🔐 Тестирую вход в систему...")
        
        login_data = {
            "email": self.user_email,
            "password": self.user_password
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
                    print(f"   Expires In: {data['expires_in']} минут")
                    print(f"   Refresh Expires In: {data['refresh_expires_in']} дней")
                    return True
                else:
                    print(f"❌ Ошибка входа: {response.status}")
                    error_data = await response.json()
                    print(f"   Детали: {error_data}")
                    return False
        except Exception as e:
            print(f"❌ Ошибка при входе: {e}")
            return False

    async def test_verify_token(self) -> bool:
        """Тест проверки токена"""
        if not self.access_token:
            print("❌ Нет access token для проверки")
            return False
        
        print("\n🔍 Тестирую проверку токена...")
        
        headers = {"Authorization": f"Bearer {self.access_token}"}
        
        try:
            async with self.session.post(
                f"{self.base_url}/auth/verify",
                headers=headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print("✅ Токен валиден")
                    print(f"   Пользователь: {data['user']['email']}")
                    print(f"   ID: {data['user']['id']}")
                    return True
                else:
                    print(f"❌ Токен невалиден: {response.status}")
                    return False
        except Exception as e:
            print(f"❌ Ошибка при проверке токена: {e}")
            return False

    async def test_protected_endpoint(self) -> bool:
        """Тест защищенного endpoint"""
        if not self.access_token:
            print("❌ Нет access token для тестирования")
            return False
        
        print("\n🔒 Тестирую защищенный endpoint...")
        
        headers = {"Authorization": f"Bearer {self.access_token}"}
        
        try:
            async with self.session.get(
                f"{self.base_url}/auth/me",
                headers=headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print("✅ Доступ к защищенному endpoint разрешен")
                    print(f"   Пользователь: {data['email']}")
                    return True
                else:
                    print(f"❌ Доступ запрещен: {response.status}")
                    return False
        except Exception as e:
            print(f"❌ Ошибка при доступе к endpoint: {e}")
            return False

    async def test_refresh_token(self) -> bool:
        """Тест обновления токена"""
        if not self.refresh_token:
            print("❌ Нет refresh token для тестирования")
            return False
        
        print("\n🔄 Тестирую обновление токена...")
        
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
                    old_token = self.access_token
                    self.access_token = data["access_token"]
                    
                    print("✅ Токен обновлен успешно")
                    print(f"   Старый Token: {old_token[:50]}...")
                    print(f"   Новый Token: {self.access_token[:50]}...")
                    print(f"   Expires In: {data['expires_in']} минут")
                    
                    # Проверяем, что новый токен работает
                    return await self.test_verify_token()
                else:
                    print(f"❌ Ошибка обновления токена: {response.status}")
                    error_data = await response.json()
                    print(f"   Детали: {error_data}")
                    return False
        except Exception as e:
            print(f"❌ Ошибка при обновлении токена: {e}")
            return False

    async def test_session_persistence(self) -> bool:
        """Тест сохранения сессии"""
        print("\n⏰ Тестирую сохранение сессии...")
        
        # Ждем немного
        print("   Ждем 5 секунд...")
        await asyncio.sleep(5)
        
        # Проверяем, что токен все еще работает
        if await self.test_verify_token():
            print("✅ Сессия сохранена")
            return True
        else:
            print("❌ Сессия потеряна")
            return False

    async def test_logout(self) -> bool:
        """Тест выхода из системы"""
        if not self.access_token:
            print("❌ Нет access token для выхода")
            return False
        
        print("\n🚪 Тестирую выход из системы...")
        
        headers = {"Authorization": f"Bearer {self.access_token}"}
        
        try:
            async with self.session.post(
                f"{self.base_url}/auth/logout",
                headers=headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print("✅ Выход выполнен успешно")
                    print(f"   Сообщение: {data.get('message', 'N/A')}")
                    
                    # Очищаем токены
                    self.access_token = None
                    self.refresh_token = None
                    return True
                else:
                    print(f"❌ Ошибка выхода: {response.status}")
                    return False
        except Exception as e:
            print(f"❌ Ошибка при выходе: {e}")
            return False

    async def run_full_test(self):
        """Запуск полного теста"""
        print("🚀 Запуск полного теста аутентификации для Cloud Run")
        print("=" * 60)
        
        tests = [
            ("Регистрация", self.test_register),
            ("Вход", self.test_login),
            ("Проверка токена", self.test_verify_token),
            ("Защищенный endpoint", self.test_protected_endpoint),
            ("Обновление токена", self.test_refresh_token),
            ("Сохранение сессии", self.test_session_persistence),
            ("Выход", self.test_logout),
        ]
        
        results = []
        
        for test_name, test_func in tests:
            try:
                result = await test_func()
                results.append((test_name, result))
            except Exception as e:
                print(f"❌ Ошибка в тесте {test_name}: {e}")
                results.append((test_name, False))
        
        # Вывод результатов
        print("\n" + "=" * 60)
        print("📊 РЕЗУЛЬТАТЫ ТЕСТОВ:")
        print("=" * 60)
        
        passed = 0
        total = len(results)
        
        for test_name, result in results:
            status = "✅ ПРОЙДЕН" if result else "❌ ПРОВАЛЕН"
            print(f"{test_name:<20} {status}")
            if result:
                passed += 1
        
        print("=" * 60)
        print(f"Итого: {passed}/{total} тестов пройдено")
        
        if passed == total:
            print("🎉 Все тесты пройдены! Аутентификация работает корректно.")
        else:
            print("⚠️  Некоторые тесты провалены. Проверьте настройки.")


async def main():
    """Главная функция"""
    import sys
    
    # URL для тестирования
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = "http://localhost:8000"
    
    print(f"🎯 Тестирую: {base_url}")
    
    async with CloudRunAuthTester(base_url) as tester:
        await tester.run_full_test()


if __name__ == "__main__":
    asyncio.run(main())
