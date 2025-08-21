#!/usr/bin/env python3
"""
Тестовый скрипт для проверки endpoint /auth/status
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_email_status():
    """Тестирует endpoint /auth/status с разными email адресами"""
    
    # Тест 1: Существующий email
    print("=== Тест 1: Существующий email ===")
    response = requests.get(f"{BASE_URL}/auth/status?email=test@example.com")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    print()
    
    # Тест 2: Несуществующий email
    print("=== Тест 2: Несуществующий email ===")
    response = requests.get(f"{BASE_URL}/auth/status?email=nonexistent@example.com")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    print()
    
    # Тест 3: Пустой email
    print("=== Тест 3: Пустой email ===")
    response = requests.get(f"{BASE_URL}/auth/status?email=")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    print()
    
    # Тест 4: Без параметра email
    print("=== Тест 4: Без параметра email ===")
    response = requests.get(f"{BASE_URL}/auth/status")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    print()

if __name__ == "__main__":
    try:
        test_email_status()
        print("✅ Все тесты завершены!")
    except requests.exceptions.ConnectionError:
        print("❌ Ошибка подключения к серверу. Убедитесь, что сервер запущен на http://localhost:8000")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
