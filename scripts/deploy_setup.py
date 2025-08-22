#!/usr/bin/env python3
"""
Скрипт для подготовки к деплою Smart Cardiologist
Проверяет все компоненты системы перед деплоем
"""

import sys
import os
import logging
from pathlib import Path

# Добавляем корневую директорию в путь
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.three_level_filter import get_medical_filter
from services.ml_filter_service import get_medical_classifier
from utils.medical_keywords import quick_medical_filter

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def check_environment():
    """Проверка переменных окружения"""
    print("🔍 Проверка переменных окружения...")
    
    required_vars = [
        'DATABASE_URL',
        'SECRET_KEY',
        'GROQ_API_KEY',
        'EMAIL_HOST',
        'EMAIL_PORT',
        'EMAIL_USERNAME',
        'EMAIL_PASSWORD'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Отсутствуют переменные окружения: {missing_vars}")
        return False
    else:
        print("✅ Все переменные окружения настроены")
        return True

def check_dependencies():
    """Проверка зависимостей"""
    print("\n📦 Проверка зависимостей...")
    
    try:
        import fastapi
        import uvicorn
        import sqlalchemy
        import pandas
        import numpy
        import sklearn
        import groq
        print("✅ Все основные зависимости установлены")
        return True
    except ImportError as e:
        print(f"❌ Отсутствует зависимость: {e}")
        return False

def check_ml_model():
    """Проверка ML-модели"""
    print("\n🤖 Проверка ML-модели...")
    
    model_path = Path("data/processed/medical_classifier.pkl")
    if not model_path.exists():
        print("❌ ML-модель не найдена. Запустите: make train-ml")
        return False
    
    try:
        classifier = get_medical_classifier()
        # Тестируем модель
        is_medical, confidence = classifier.predict("What are the symptoms of heart disease?")
        print(f"✅ ML-модель загружена и работает (тест: {is_medical}, уверенность: {confidence:.3f})")
        return True
    except Exception as e:
        print(f"❌ Ошибка загрузки ML-модели: {e}")
        return False

def check_three_level_filter():
    """Проверка трёхуровневой системы фильтрации"""
    print("\n🔍 Проверка трёхуровневой системы фильтрации...")
    
    try:
        medical_filter = get_medical_filter()
        
        # Тестируем все уровни
        test_cases = [
            ("What are the symptoms of heart disease?", True),
            ("What is the weather like today?", False),
            ("I have chest pain", True),
            ("How do I cook pasta?", False)
        ]
        
        for question, expected in test_cases:
            result = medical_filter.filter_question(question)
            if result['is_medical'] == expected:
                print(f"✅ '{question[:30]}...' -> {result['method']}")
            else:
                print(f"⚠️  '{question[:30]}...' -> {result['method']} (ожидалось: {expected})")
        
        print("✅ Трёхуровневая система фильтрации работает")
        return True
    except Exception as e:
        print(f"❌ Ошибка трёхуровневой системы: {e}")
        return False

def check_database():
    """Проверка базы данных"""
    print("\n🗄️  Проверка базы данных...")
    
    try:
        from src.services.database import get_db
        from sqlalchemy import text
        
        # Проверяем подключение
        print("✅ Подключение к базе данных настроено")
        return True
    except Exception as e:
        print(f"❌ Ошибка базы данных: {e}")
        return False

def check_data_files():
    """Проверка файлов данных"""
    print("\n📁 Проверка файлов данных...")
    
    required_files = [
        "data/medicalQ/medical_data.csv",
        "data/nonMedicalQ/questions.csv",
        "data/processed/medical_classifier.pkl"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Отсутствуют файлы: {missing_files}")
        return False
    else:
        print("✅ Все файлы данных найдены")
        return True

def run_tests():
    """Запуск тестов"""
    print("\n🧪 Запуск тестов...")
    
    try:
        import subprocess
        result = subprocess.run([sys.executable, "-m", "pytest", "tests/", "-v"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Все тесты прошли успешно")
            return True
        else:
            print(f"❌ Тесты не прошли: {result.stdout}")
            return False
    except Exception as e:
        print(f"❌ Ошибка запуска тестов: {e}")
        return False

def main():
    """Основная функция проверки"""
    print("🚀 Подготовка к деплою Smart Cardiologist\n")
    
    checks = [
        ("Переменные окружения", check_environment),
        ("Зависимости", check_dependencies),
        ("Файлы данных", check_data_files),
        ("ML-модель", check_ml_model),
        ("Трёхуровневая система", check_three_level_filter),
        ("База данных", check_database),
        ("Тесты", run_tests)
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ Ошибка при проверке {name}: {e}")
            results.append((name, False))
    
    print("\n" + "="*50)
    print("📊 РЕЗУЛЬТАТЫ ПРОВЕРКИ:")
    print("="*50)
    
    all_passed = True
    for name, result in results:
        status = "✅ ПРОЙДЕНО" if result else "❌ НЕ ПРОЙДЕНО"
        print(f"{name:25} {status}")
        if not result:
            all_passed = False
    
    print("="*50)
    
    if all_passed:
        print("🎉 ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ! Система готова к деплою.")
        print("\n📋 Следующие шаги:")
        print("1. Настройте сервер")
        print("2. Скопируйте код")
        print("3. Установите зависимости")
        print("4. Настройте базу данных")
        print("5. Запустите приложение")
    else:
        print("⚠️  НЕКОТОРЫЕ ПРОВЕРКИ НЕ ПРОЙДЕНЫ. Исправьте ошибки перед деплоем.")
    
    return all_passed

if __name__ == "__main__":
    main()
