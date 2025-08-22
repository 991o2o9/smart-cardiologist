#!/usr/bin/env python3
"""
Скрипт для тестирования трёхуровневой системы фильтрации медицинских вопросов
"""

import sys
import os
import logging

# Добавляем корневую директорию в путь
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.three_level_filter import get_medical_filter
from utils.medical_keywords import quick_medical_filter
from services.ml_filter_service import get_medical_classifier

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_three_level_filter():
    """Тестирование трёхуровневой системы фильтрации"""
    print("🧪 Тестирование трёхуровневой системы фильтрации медицинских вопросов\n")
    
    # Получаем фильтр
    medical_filter = get_medical_filter()
    
    # Тестовые вопросы
    test_questions = [
        # Явно медицинские вопросы (должны пройти быстрый фильтр)
        ("What are the symptoms of heart disease?", True),
        ("How can I lower my blood pressure?", True),
        ("Is my chest pain serious?", True),
        ("What causes arrhythmia?", True),
        ("Can stress affect my heart health?", True),
        
        # Немедицинские вопросы (должны быть отклонены)
        ("What is the weather like today?", False),
        ("How do I cook pasta?", False),
        ("What time is the movie?", False),
        ("How do I fix my computer?", False),
        ("What is the capital of France?", False),
        
        # Сложные случаи (могут потребовать ML или LLM)
        ("I feel tired and have a headache", True),
        ("My heart is beating fast when I exercise", True),
        ("I have pain in my chest after eating", True),
        ("What should I do about my anxiety?", True),
        ("How do I improve my fitness?", False),
        ("I have trouble sleeping", True),
        ("What's the best way to lose weight?", False),
        ("My blood pressure is 140/90", True),
        
        # Русские вопросы
        ("У меня болит сердце", True),
        ("Как снизить давление?", True),
        ("Что делать при боли в груди?", True),
        ("Какая погода сегодня?", False),
        ("Как приготовить борщ?", False),
    ]
    
    print("Результаты тестирования:")
    print("=" * 80)
    
    for i, (question, expected) in enumerate(test_questions, 1):
        print(f"\n{i:2d}. Вопрос: '{question}'")
        print(f"    Ожидается: {'МЕДИЦИНСКИЙ' if expected else 'НЕ МЕДИЦИНСКИЙ'}")
        
        # Тестируем трёхуровневую систему
        result = medical_filter.filter_question(question)
        
        print(f"    Результат: {'✅ МЕДИЦИНСКИЙ' if result['is_medical'] else '❌ НЕ МЕДИЦИНСКИЙ'}")
        print(f"    Метод: {result['method']}")
        print(f"    Уверенность: {result['confidence']:.3f}")
        
        # Проверяем правильность
        if result['is_medical'] == expected:
            print(f"    Статус: ✅ ПРАВИЛЬНО")
        else:
            print(f"    Статус: ❌ ОШИБКА")
    
    print("\n" + "=" * 80)
    print("Тестирование завершено!")

def test_individual_components():
    """Тестирование отдельных компонентов"""
    print("\n🔧 Тестирование отдельных компонентов:\n")
    
    # Тест быстрого фильтра
    print("1. Быстрый фильтр (ключевые слова):")
    test_text = "What are the symptoms of heart disease?"
    is_medical, confidence = quick_medical_filter(test_text)
    print(f"   '{test_text}' -> {'МЕДИЦИНСКИЙ' if is_medical else 'НЕ МЕДИЦИНСКИЙ'} (уверенность: {confidence:.3f})")
    
    # Тест ML-классификатора
    print("\n2. ML-классификатор:")
    classifier = get_medical_classifier()
    is_medical, confidence = classifier.predict(test_text)
    print(f"   '{test_text}' -> {'МЕДИЦИНСКИЙ' if is_medical else 'НЕ МЕДИЦИНСКИЙ'} (уверенность: {confidence:.3f})")

def main():
    """Основная функция"""
    print("🚀 Запуск тестирования трёхуровневой системы фильтрации\n")
    
    try:
        # Тестируем отдельные компоненты
        test_individual_components()
        
        # Тестируем полную систему
        test_three_level_filter()
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании: {e}")
        logging.error(f"Ошибка при тестировании: {e}", exc_info=True)

if __name__ == "__main__":
    main()
