#!/bin/bash

# Скрипт деплоя Smart Cardiologist
set -e

echo "🚀 Начинаем деплой Smart Cardiologist..."

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Функция для вывода с цветом
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Проверка наличия Docker
if ! command -v docker &> /dev/null; then
    print_error "Docker не установлен. Установите Docker перед деплоем."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose не установлен. Установите Docker Compose перед деплоем."
    exit 1
fi

print_status "Docker и Docker Compose найдены"

# Проверка переменных окружения
if [ ! -f .env ]; then
    print_warning "Файл .env не найден. Создаем пример..."
    cat > .env << EOF
# База данных
DB_PASSWORD=secure_password_123

# Безопасность
SECRET_KEY=your_secret_key_here_change_this

# API ключи
GROQ_API_KEY=your_groq_api_key_here

# Email настройки
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USERNAME=your_email@gmail.com
EMAIL_PASSWORD=your_email_password
EOF
    print_warning "Создан файл .env. Отредактируйте его перед деплоем!"
    exit 1
fi

print_status "Переменные окружения настроены"

# Загрузка переменных окружения
source .env

# Проверка обязательных переменных
required_vars=("SECRET_KEY" "GROQ_API_KEY" "EMAIL_HOST" "EMAIL_USERNAME" "EMAIL_PASSWORD")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        print_error "Переменная $var не установлена в .env файле"
        exit 1
    fi
done

print_status "Все обязательные переменные окружения установлены"

# Проверка готовности к деплою
print_status "Проверка готовности к деплою..."
python scripts/deploy_setup.py

if [ $? -ne 0 ]; then
    print_error "Проверка готовности не прошла. Исправьте ошибки перед деплоем."
    exit 1
fi

print_status "Система готова к деплою"

# Остановка существующих контейнеров
print_status "Остановка существующих контейнеров..."
docker-compose down 2>/dev/null || true

# Очистка старых образов (опционально)
if [ "$1" = "--clean" ]; then
    print_status "Очистка старых образов..."
    docker system prune -f
fi

# Сборка Docker образа
print_status "Сборка Docker образа..."
docker build -t smart-cardiologist .

if [ $? -ne 0 ]; then
    print_error "Ошибка сборки Docker образа"
    exit 1
fi

print_status "Docker образ собран успешно"

# Запуск контейнеров
print_status "Запуск контейнеров..."
docker-compose up -d

if [ $? -ne 0 ]; then
    print_error "Ошибка запуска контейнеров"
    exit 1
fi

print_status "Контейнеры запущены"

# Ожидание готовности сервисов
print_status "Ожидание готовности сервисов..."
sleep 10

# Проверка здоровья приложения
print_status "Проверка здоровья приложения..."
for i in {1..30}; do
    if curl -f http://localhost:8000/health >/dev/null 2>&1; then
        print_status "Приложение готово!"
        break
    fi
    if [ $i -eq 30 ]; then
        print_error "Приложение не готово после 30 попыток"
        docker-compose logs app
        exit 1
    fi
    print_status "Ожидание... ($i/30)"
    sleep 2
done

# Применение миграций базы данных
print_status "Применение миграций базы данных..."
docker-compose exec app alembic upgrade head

if [ $? -ne 0 ]; then
    print_warning "Ошибка применения миграций (возможно, база данных уже обновлена)"
fi

# Финальная проверка
print_status "Финальная проверка..."
curl -f http://localhost:8000/health >/dev/null 2>&1

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 ДЕПЛОЙ ЗАВЕРШЕН УСПЕШНО!"
    echo ""
    echo "📊 Информация о деплое:"
    echo "   🌐 Приложение: http://localhost:8000"
    echo "   📚 API документация: http://localhost:8000/docs"
    echo "   🗄️  База данных: localhost:5432"
    echo "   🔄 Redis: localhost:6379"
    echo ""
    echo "📋 Полезные команды:"
    echo "   Логи: make docker-logs"
    echo "   Остановка: make docker-stop"
    echo "   Перезапуск: make docker-run"
    echo ""
else
    print_error "Финальная проверка не прошла"
    docker-compose logs app
    exit 1
fi
