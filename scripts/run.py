import sys
import os
import uvicorn
from pathlib import Path

# Добавляем корневую директорию в PYTHONPATH
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.settings import settings

def main():
    """Основная функция запуска"""
    try:
        # Проверяем настройки
        settings.validate()
        
        print("🏥 Запуск Smart Cardiologist API...")
        print(f"📍 Хост: {settings.HOST}")
        print(f"🔌 Порт: {settings.PORT}")
        print(f"🐛 Debug: {settings.DEBUG}")
        print(f"📊 Rate Limit: {settings.RATE_LIMIT} запросов/мин")
        print(f"💾 Cache TTL: {settings.CACHE_TTL} сек")
        print("-" * 50)
        
        # Запускаем сервер
        uvicorn.run(
            "src.main:app",
            host=settings.HOST,
            port=settings.PORT,
            reload=settings.DEBUG,
            log_level=settings.LOG_LEVEL.lower()
        )
        
    except ValueError as e:
        print(f"❌ Ошибка конфигурации: {e}")
        print("💡 Проверьте файл .env и переменные окружения")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Сервер остановлен")
    except Exception as e:
        print(f"❌ Ошибка запуска: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
