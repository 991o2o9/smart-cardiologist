#!/usr/bin/env python3
"""
Скрипт для тестирования API авторизации
"""
import asyncio
import aiohttp
import json
import sys
from typing import Optional

# URL базового API
BASE_URL = "http://localhost:8000/api/v1"

# Тестовые данные
TEST_USER = {
    "email": "test@example.com",
    "password": "testpassword123"
}

class AuthAPITester:
    """Класс для тестирования API авторизации"""
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.access_token: Optional[str] = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def test_register(self) -> bool:
        """Тест регистрации пользователя"""
        print("🔐 Тестирование регистрации...")
        
        try:
            async with self.session.post(
                f"{BASE_URL}/auth/register",
                json=TEST_USER
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Регистрация успешна: {data['message']}")
                    return True
                else:
                    error_data = await response.json()
                    print(f"❌ Ошибка регистрации: {error_data}")
                    return False
        except Exception as e:
            print(f"❌ Ошибка при регистрации: {e}")
            return False
    
    async def test_activate(self, activation_code: str) -> bool:
        """Тест активации аккаунта"""
        print(f"🔑 Тестирование активации с кодом: {activation_code}")
        
        try:
            async with self.session.post(
                f"{BASE_URL}/auth/activate",
                json={
                    "email": TEST_USER["email"],
                    "activation_code": activation_code
                }
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Активация успешна: {data['message']}")
                    return True
                else:
                    error_data = await response.json()
                    print(f"❌ Ошибка активации: {error_data}")
                    return False
        except Exception as e:
            print(f"❌ Ошибка при активации: {e}")
            return False
    
    async def test_login(self) -> bool:
        """Тест входа в систему"""
        print("🔓 Тестирование входа...")
        
        try:
            async with self.session.post(
                f"{BASE_URL}/auth/login",
                json=TEST_USER
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    self.access_token = data["access_token"]
                    print(f"✅ Вход успешен! Токен получен")
                    return True
                else:
                    error_data = await response.json()
                    print(f"❌ Ошибка входа: {error_data}")
                    return False
        except Exception as e:
            print(f"❌ Ошибка при входе: {e}")
            return False
    
    async def test_protected_endpoint(self) -> bool:
        """Тест защищенного endpoint"""
        if not self.access_token:
            print("❌ Нет токена для тестирования защищенного endpoint")
            return False
        
        print("🛡️ Тестирование защищенного endpoint...")
        
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            async with self.session.get(
                f"{BASE_URL}/auth/me",
                headers=headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Защищенный endpoint доступен: {data['email']}")
                    return True
                else:
                    error_data = await response.json()
                    print(f"❌ Ошибка доступа: {error_data}")
                    return False
        except Exception as e:
            print(f"❌ Ошибка при тестировании защищенного endpoint: {e}")
            return False
    
    async def test_cardio_analysis(self) -> bool:
        """Тест анализа кардио-ассистента"""
        if not self.access_token:
            print("❌ Нет токена для тестирования кардио-анализа")
            return False
        
        print("💓 Тестирование кардио-анализа...")
        
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            analysis_data = {
                "age": 45,
                "pulse": 85,
                "risk": "средний",
                "symptoms": "одышка при физической нагрузке"
            }
            
            async with self.session.post(
                f"{BASE_URL}/cardio-assistant/",
                json=analysis_data,
                headers=headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Кардио-анализ успешен! Кеширован: {data['cached']}")
                    return True
                else:
                    error_data = await response.json()
                    print(f"❌ Ошибка кардио-анализа: {error_data}")
                    return False
        except Exception as e:
            print(f"❌ Ошибка при тестировании кардио-анализа: {e}")
            return False
    
    async def test_history(self) -> bool:
        """Тест получения истории анализов"""
        if not self.access_token:
            print("❌ Нет токена для тестирования истории")
            return False
        
        print("📊 Тестирование получения истории...")
        
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            async with self.session.get(
                f"{BASE_URL}/cardio-assistant/history",
                headers=headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ История получена! Количество записей: {len(data)}")
                    return True
                else:
                    error_data = await response.json()
                    print(f"❌ Ошибка получения истории: {error_data}")
                    return False
        except Exception as e:
            print(f"❌ Ошибка при получении истории: {e}")
            return False
    
    async def run_all_tests(self) -> bool:
        """Запуск всех тестов"""
        print("🚀 Запуск тестов API авторизации...")
        print("=" * 50)
        
        tests_passed = 0
        total_tests = 6
        
        # Тест 1: Регистрация
        if await self.test_register():
            tests_passed += 1
        
        # Тест 2: Активация (с ручным вводом кода)
        print("\n📧 Проверьте email и введите код активации:")
        activation_code = input("Код активации: ").strip()
        
        if await self.test_activate(activation_code):
            tests_passed += 1
        
        # Тест 3: Вход
        if await self.test_login():
            tests_passed += 1
        
        # Тест 4: Защищенный endpoint
        if await self.test_protected_endpoint():
            tests_passed += 1
        
        # Тест 5: Кардио-анализ
        if await self.test_cardio_analysis():
            tests_passed += 1
        
        # Тест 6: История
        if await self.test_history():
            tests_passed += 1
        
        print("\n" + "=" * 50)
        print(f"📊 Результаты тестов: {tests_passed}/{total_tests} пройдено")
        
        if tests_passed == total_tests:
            print("🎉 Все тесты пройдены успешно!")
            return True
        else:
            print("⚠️ Некоторые тесты не прошли")
            return False


async def main():
    """Основная функция"""
    print("Smart Cardiologist - Тестирование API авторизации")
    print("Убедитесь, что приложение запущено на http://localhost:8000")
    print()
    
    try:
        async with AuthAPITester() as tester:
            success = await tester.run_all_tests()
            sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️ Тестирование прервано пользователем")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Критическая ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
