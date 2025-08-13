#!/usr/bin/env python3
"""
Скрипт для настройки переменных окружения
"""
import os
import shutil

def setup_environment():
    """Настраивает файл .env из env.example"""
    
    # Проверяем, существует ли уже файл .env
    if os.path.exists('.env'):
        print("Файл .env уже существует!")
        response = input("Хотите перезаписать его? (y/N): ")
        if response.lower() != 'y':
            print("Настройка отменена.")
            return
    
    # Копируем env.example в .env
    if os.path.exists('env.example'):
        shutil.copy('env.example', '.env')
        print("✅ Файл .env создан из env.example")
        print("\n📝 Не забудьте отредактировать файл .env и указать ваш GROQ_API_KEY!")
    else:
        print("❌ Файл env.example не найден!")
        print("Создайте файл .env вручную на основе env.example")

if __name__ == "__main__":
    setup_environment()
