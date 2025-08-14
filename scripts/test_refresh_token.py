#!/usr/bin/env python3
"""
Тестовый скрипт для проверки refresh token системы
"""

import asyncio
import httpx
import json
from typing import Dict, Any


class AuthTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient()
        self.access_token = None
        self.refresh_token = None
    
    async def test_register(self, email: str, password: str) -> Dict[str, Any]:
        """Тест регистрации"""
        print(f"🔐 Тестируем регистрацию пользователя: {email}")
        
        response = await self.client.post(
            f"{self.base_url}/auth/register",
            json={"email": email, "password": password}
        )
        
        print(f"Статус: {response.status_code}")
        print(f"Ответ: {response.json()}")
        print()
        
        return response.json()
    
    async def test_activate(self, email: str, activation_code: str) -> Dict[str, Any]:
        """Тест активации (симуляция)"""
        print(f"✅ Тестируем активацию аккаунта: {email}")
        print(f"Код активации: {activation_code}")
        print("(В реальном приложении код приходит на email)")
        print()
        
        # В реальном тесте нужно получить код из email
        # Здесь просто показываем, что код нужен
        return {"message": "Активация требует реального кода из email"}
    
    async def test_login(self, email: str, password: str) -> Dict[str, Any]:
        """Тест входа"""
        print(f"🚪 Тестируем вход пользователя: {email}")
        
        response = await self.client.post(
            f"{self.base_url}/auth/login",
            json={"email": email, "password": password}
        )
        
        print(f"Статус: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            self.access_token = data["access_token"]
            self.refresh_token = data["refresh_token"]
            
            print(f"✅ Вход успешен!")
            print(f"Access Token: {self.access_token[:50]}...")
            print(f"Refresh Token: {self.refresh_token[:50]}...")
            print(f"Access Token expires in: {data['expires_in']} минут")
            print(f"Refresh Token expires in: {data['refresh_expires_in']} дней")
        else:
            print(f"❌ Ошибка входа: {response.json()}")
        
        print()
        return response.json()
    
    async def test_refresh_token(self) -> Dict[str, Any]:
        """Тест обновления токена"""
        if not self.refresh_token:
            print("❌ Нет refresh token для тестирования")
            return {}
        
        print("🔄 Тестируем обновление access token")
        
        response = await self.client.post(
            f"{self.base_url}/auth/refresh",
            json={"refresh_token": self.refresh_token}
        )
        
        print(f"Статус: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            self.access_token = data["access_token"]
            
            print(f"✅ Токен обновлен!")
            print(f"Новый Access Token: {self.access_token[:50]}...")
            print(f"Expires in: {data['expires_in']} минут")
        else:
            print(f"❌ Ошибка обновления: {response.json()}")
        
        print()
        return response.json()
    
    async def test_protected_endpoint(self) -> Dict[str, Any]:
        """Тест защищенного endpoint"""
        if not self.access_token:
            print("❌ Нет access token для тестирования")
            return {}
        
        print("🔒 Тестируем защищенный endpoint (/auth/me)")
        
        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = await self.client.get(
            f"{self.base_url}/auth/me",
            headers=headers
        )
        
        print(f"Статус: {response.status_code}")
        
        if response.status_code == 200:
            print(f"✅ Доступ разрешен: {response.json()}")
        else:
            print(f"❌ Доступ запрещен: {response.json()}")
        
        print()
        return response.json()
    
    async def test_logout(self) -> Dict[str, Any]:
        """Тест выхода"""
        if not self.access_token:
            print("❌ Нет access token для тестирования")
            return {}
        
        print("🚪 Тестируем выход из системы")
        
        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = await self.client.post(
            f"{self.base_url}/auth/logout",
            headers=headers
        )
        
        print(f"Статус: {response.status_code}")
        
        if response.status_code == 200:
            print(f"✅ Выход успешен: {response.json()}")
            # Очищаем токены
            self.access_token = None
            self.refresh_token = None
        else:
            print(f"❌ Ошибка выхода: {response.json()}")
        
        print()
        return response.json()
    
    async def test_cardio_analysis(self) -> Dict[str, Any]:
        """Тест кардио-анализа с шифрованием"""
        if not self.access_token:
            print("❌ Нет access token для тестирования")
            return {}
        
        print("💓 Тестируем кардио-анализ с шифрованием данных")
        
        headers = {"Authorization": f"Bearer {self.access_token}"}
        data = {
            "age": 45,
            "pulse": 85,
            "risk": "средний",
            "symptoms": "Боли в груди, одышка при физической нагрузке"
        }
        
        response = await self.client.post(
            f"{self.base_url}/cardio-assistant/",
            json=data,
            headers=headers
        )
        
        print(f"Статус: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Анализ выполнен: {result['cached']}")
            print(f"Ответ AI: {result['response'][:100]}...")
        else:
            print(f"❌ Ошибка анализа: {response.json()}")
        
        print()
        return response.json()
    
    async def test_heart_prediction(self) -> Dict[str, Any]:
        """Тест предсказания сердечных заболеваний с шифрованием"""
        if not self.access_token:
            print("❌ Нет access token для тестирования")
            return {}
        
        print("❤️ Тестируем предсказание сердечных заболеваний с шифрованием")
        
        headers = {"Authorization": f"Bearer {self.access_token}"}
        data = {
            "age": 55,
            "sex": 1,
            "cp": 2,
            "trestbps": 140,
            "chol": 250,
            "fbs": 1,
            "restecg": 1,
            "thalach": 150,
            "exang": 0,
            "oldpeak": 1.5,
            "slope": 1,
            "ca": 1,
            "thal": 2,
            "pulse": 80
        }
        
        response = await self.client.post(
            f"{self.base_url}/heart-prediction/predict",
            json=data,
            headers=headers
        )
        
        print(f"Статус: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Предсказание выполнено:")
            print(f"Риск: {result['risk']}")
            print(f"Вероятность: {result['probability']:.2%}")
        else:
            print(f"❌ Ошибка предсказания: {response.json()}")
        
        print()
        return response.json()
    
    async def run_all_tests(self):
        """Запуск всех тестов"""
        print("🧪 ЗАПУСК ТЕСТОВ REFRESH TOKEN СИСТЕМЫ")
        print("=" * 50)
        
        # Тест 1: Регистрация
        await self.test_register("test@example.com", "securepass123")
        
        # Тест 2: Активация (симуляция)
        await self.test_activate("test@example.com", "123456")
        
        # Тест 3: Вход
        await self.test_login("test@example.com", "securepass123")
        
        # Тест 4: Защищенный endpoint
        await self.test_protected_endpoint()
        
        # Тест 5: Обновление токена
        await self.test_refresh_token()
        
        # Тест 6: Кардио-анализ с шифрованием
        await self.test_cardio_analysis()
        
        # Тест 7: Предсказание с шифрованием
        await self.test_heart_prediction()
        
        # Тест 8: Выход
        await self.test_logout()
        
        print("🏁 ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
        print("=" * 50)
    
    async def close(self):
        """Закрытие клиента"""
        await self.client.aclose()


async def main():
    """Основная функция"""
    tester = AuthTester()
    
    try:
        await tester.run_all_tests()
    finally:
        await tester.close()


if __name__ == "__main__":
    asyncio.run(main())
