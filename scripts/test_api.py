import sys
import requests
import json
import time
from pathlib import Path

# Добавляем корневую директорию в PYTHONPATH
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

BASE_URL = "http://localhost:8000"

def test_api():
    """Тестирование API"""
    print("🧪 Тестирование Smart Cardiologist API")
    print("=" * 50)
    
    # Тест 1: Корневой endpoint
    print("\n1️⃣ Тест корневого endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Статус: {response.status_code}")
            print(f"   📝 Сообщение: {data.get('message')}")
            print(f"   🔢 Версия: {data.get('version')}")
        else:
            print(f"   ❌ Ошибка: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Ошибка подключения: {e}")
        return
    
    # Тест 2: Health check
    print("\n2️⃣ Тест health check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Статус: {response.status_code}")
            print(f"   🏥 Состояние: {data.get('status')}")
        else:
            print(f"   ❌ Ошибка: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
    
    # Тест 3: Cardio Assistant
    print("\n3️⃣ Тест Cardio Assistant...")
    cardio_data = {
        "age": 45,
        "pulse": 85,
        "risk": "средний",
        "symptoms": "одышка при физической нагрузке, усталость"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/cardio-assistant/",
            json=cardio_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Статус: {response.status_code}")
            print(f"   📦 Кешированный: {data.get('cached')}")
            print(f"   💬 Ответ (первые 100 символов): {data.get('response', '')[:100]}...")
        elif response.status_code == 500:
            print(f"   ⚠️  Серверная ошибка: {response.status_code}")
            print(f"   💡 Возможно, не настроен GROQ_API_KEY")
        else:
            print(f"   ❌ Ошибка: {response.status_code}")
            print(f"   📝 Ответ: {response.text}")
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
    
    # Тест 4: Heart Prediction
    print("\n4️⃣ Тест Heart Prediction...")
    heart_data = {
        "age": 45,
        "sex": 1,
        "cp": 1,
        "trestbps": 130,
        "chol": 250,
        "fbs": 0,
        "restecg": 0,
        "thalach": 150,
        "exang": 0,
        "oldpeak": 2.0,
        "slope": 1,
        "ca": 0,
        "thal": 1,
        "pulse": 85
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/heart-prediction/predict",
            json=heart_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Статус: {response.status_code}")
            print(f"   🎯 Риск: {data.get('risk')}")
            print(f"   📊 Вероятность: {data.get('probability')}")
        elif response.status_code == 500:
            print(f"   ⚠️  Серверная ошибка: {response.status_code}")
            print(f"   💡 Возможно, модель не загружена")
        else:
            print(f"   ❌ Ошибка: {response.status_code}")
            print(f"   📝 Ответ: {response.text}")
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
    
    # Тест 5: Rate Limiting
    print("\n5️⃣ Тест Rate Limiting...")
    print("   Отправляем 6 запросов подряд (лимит: 5 в минуту):")
    
    for i in range(6):
        try:
            response = requests.post(
                f"{BASE_URL}/cardio-assistant/",
                json=cardio_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 429:
                print(f"   Запрос {i+1}: ❌ Rate Limited (429)")
            elif response.status_code == 200:
                print(f"   Запрос {i+1}: ✅ Успешно (200)")
            else:
                print(f"   Запрос {i+1}: ⚠️  Статус {response.status_code}")
                
            time.sleep(0.5)  # Небольшая пауза
            
        except Exception as e:
            print(f"   Запрос {i+1}: ❌ Ошибка: {e}")
    
    print("\n✅ Тестирование завершено!")

if __name__ == "__main__":
    test_api()
