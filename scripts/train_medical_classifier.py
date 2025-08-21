#!/usr/bin/env python3
"""
Скрипт для обучения ML-модели классификации медицинских вопросов
"""

import sys
import os
import logging

# Добавляем корневую директорию в путь
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.ml_filter_service import MedicalQuestionClassifier

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    """Основная функция обучения модели"""
    print("🚀 Начинаем обучение ML-модели для классификации медицинских вопросов...")
    
    # Создаем классификатор
    classifier = MedicalQuestionClassifier()
    
    # Проверяем наличие данных
    medical_path = "data/medicalQ/medical_questions.csv"
    non_medical_path = "data/nonMedicalQ/questions.csv"
    
    if not os.path.exists(medical_path):
        print(f"❌ Файл с медицинскими вопросами не найден: {medical_path}")
        return
    
    if not os.path.exists(non_medical_path):
        print(f"❌ Файл с немедицинскими вопросами не найден: {non_medical_path}")
        return
    
    print("✅ Файлы данных найдены")
    
    # Обучаем модель
    try:
        classifier.train_model()
        print("✅ Модель успешно обучена и сохранена!")
        
        # Тестируем модель на нескольких примерах
        print("\n🧪 Тестируем модель на примерах:")
        
        test_questions = [
            "What are the symptoms of heart disease?",
            "How can I lower my blood pressure?",
            "What is the weather like today?",
            "How do I cook pasta?",
            "Is my chest pain serious?",
            "What time is the movie?",
            "Can stress affect my heart?",
            "How do I fix my computer?"
        ]
        
        for question in test_questions:
            is_medical, confidence = classifier.predict(question)
            status = "✅ МЕДИЦИНСКИЙ" if is_medical else "❌ НЕ МЕДИЦИНСКИЙ"
            print(f"'{question}' -> {status} (уверенность: {confidence:.3f})")
            
    except Exception as e:
        print(f"❌ Ошибка при обучении модели: {e}")
        logging.error(f"Ошибка при обучении модели: {e}", exc_info=True)

if __name__ == "__main__":
    main()
