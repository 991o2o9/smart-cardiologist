#!/bin/bash

# Скрипт для деплоя исправлений аутентификации на Cloud Run

set -euo pipefail

echo "🚀 Деплой исправлений аутентификации для Cloud Run"
echo "=================================================="

# Проверяем, что мы в правильной директории
if [ ! -f "cloudbuild.yaml" ]; then
    echo "❌ Ошибка: cloudbuild.yaml не найден. Запустите скрипт из корневой директории проекта."
    exit 1
fi

# Проверяем наличие gcloud
if ! command -v gcloud &> /dev/null; then
    echo "❌ Ошибка: gcloud не установлен. Установите Google Cloud SDK."
    exit 1
fi

# Проверяем аутентификацию
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo "❌ Ошибка: Не авторизован в gcloud. Выполните 'gcloud auth login'"
    exit 1
fi

# Получаем текущий проект
PROJECT_ID=$(gcloud config get-value project)
if [ -z "$PROJECT_ID" ]; then
    echo "❌ Ошибка: Не установлен проект. Выполните 'gcloud config set project YOUR_PROJECT_ID'"
    exit 1
fi

echo "📋 Проект: $PROJECT_ID"

# Запрашиваем подтверждение
read -p "Продолжить деплой? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Деплой отменен"
    exit 1
fi

echo "🔨 Запуск сборки и деплоя..."

# Запускаем сборку
gcloud builds submit --config cloudbuild.yaml

echo "✅ Деплой завершен успешно!"
echo ""
echo "📝 Следующие шаги:"
echo "1. Протестируйте аутентификацию:"
echo "   python scripts/test_cloud_run_auth.py https://your-cloud-run-url.com"
echo ""
echo "2. Проверьте логи Cloud Run:"
echo "   gcloud logging read 'resource.type=cloud_run_revision' --limit=50"
echo ""
echo "3. Обновите клиентскую сторону согласно документации:"
echo "   docs/CLOUD_RUN_AUTH_FIX.md"
echo ""
echo "🎉 Исправления аутентификации развернуты!"
