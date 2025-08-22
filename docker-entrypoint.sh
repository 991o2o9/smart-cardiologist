#!/bin/bash
set -e

echo "🚀 Запуск entrypoint..."

# Обучаем ML модель, если её нет
if [ ! -f "data/processed/medical_classifier.pkl" ]; then
  echo "⚙️  Обучение ML модели..."
  python scripts/train_medical_classifier.py || echo "⚠️  Не удалось обучить модель"
fi

# Запускаем приложение
echo "✅ Старт uvicorn..."
exec uvicorn main:app --host 0.0.0.0 --port 8000
