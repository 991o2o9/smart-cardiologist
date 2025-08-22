# Используем официальный Python образ
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    bash \
    && rm -rf /var/lib/apt/lists/*

# Копируем файлы зависимостей
COPY requirements.txt .

# Устанавливаем Python зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код приложения
COPY . .

# Делаем start.sh исполняемым (после COPY!)
RUN chmod +x scripts/start.sh

# Создаем директории для данных
RUN mkdir -p data/processed data/medicalQ data/nonMedicalQ logs

# ⚠️ Обучение модели — лучше вынести в CI/CD (build будет долгий). 
# Но если нужно прямо в Docker:
RUN test -f data/processed/medical_classifier.pkl || python scripts/train_medical_classifier.py

# Создаем пользователя для безопасности
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app
USER app

# Открываем порт
EXPOSE 8000

# Запускаем через start.sh
CMD ["bash", "scripts/start.sh"]
