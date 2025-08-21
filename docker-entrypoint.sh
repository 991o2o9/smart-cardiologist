#!/bin/bash
set -e

echo "🚀 Запуск контейнера..."

if [ ! -f "data/processed/medical_classifier.pkl" ]; then
    echo "⚡ Модель не найдена. Обучаем..."
    python scripts/train_medical_classifier.py
else
    echo "✅ Модель найдена, обучение не требуется."
fi

echo "🚀 Запускаем приложение..."
exec uvicorn src.main:app --host 0.0.0.0 --port 8000
