# Руководство по использованию Smart Cardiologist API 📚

## Быстрый старт

### 1. Запуск сервера

```bash
# Установка зависимостей
pip install -r requirements.txt

# Настройка переменных окружения
python scripts/setup_env.py

# Обучение модели (опционально)
python scripts/train_model.py

# Запуск сервера
python scripts/run.py
```

### 2. Проверка работоспособности

```bash
# Проверка основного endpoint
curl http://localhost:8000/

# Проверка здоровья сервиса
curl http://localhost:8000/health
```

## API Endpoints

### Cardio Assistant

#### Получить анализ от AI кардиолога

**Endpoint:** `POST /cardio-assistant/`

**Описание:** Получает анализ состояния пациента от AI кардиолога на основе предоставленных данных.

**Запрос:**
```json
{
  "age": 45,
  "pulse": 85,
  "risk": "средний",
  "symptoms": "одышка при физической нагрузке, усталость"
}
```

**Ответ:**
```json
{
  "cached": false,
  "response": "**Краткое резюме (с точки зрения кардиолога)**\n\n- **Возраст 45 лет** – возраст, когда начинается активный процесс накопления факторов риска...\n\n## Рекомендации:\n1. Регулярные физические нагрузки\n2. Контроль артериального давления\n3. Консультация кардиолога..."
}
```

**Пример с curl:**
```bash
curl -X POST "http://localhost:8000/cardio-assistant/" \
  -H "Content-Type: application/json" \
  -d '{
    "age": 45,
    "pulse": 85,
    "risk": "средний",
    "symptoms": "одышка при физической нагрузке, усталость"
  }'
```

#### Проверка здоровья сервиса

**Endpoint:** `GET /cardio-assistant/health`

**Описание:** Проверяет состояние AI сервиса, кеша и rate limiter.

**Ответ:**
```json
{
  "status": "healthy",
  "ai_service": true,
  "cache_stats": {
    "size": 5,
    "ttl": 300,
    "expired_cleaned": 2
  },
  "rate_limiter_stats": {
    "max_requests": 5,
    "window_seconds": 60,
    "active_identifiers": 3,
    "total_requests": 15
  }
}
```

### Heart Prediction

#### Предсказать риск сердечных заболеваний

**Endpoint:** `POST /heart-prediction/predict`

**Описание:** Предсказывает риск сердечных заболеваний на основе медицинских параметров.

**Запрос:**
```json
{
  "age": 45,
  "sex": 1,
  "cp": 1,
  "trestbps": 130,
  "chol": 250,
  "fbs": 0,
  "restecg": 0,
  "thalach": 150,
  "exang": 0,
  "oldpeak": 2.0,
  "slope": 1,
  "ca": 0,
  "thal": 1,
  "pulse": 85
}
```

**Ответ:**
```json
{
  "risk": 1,
  "probability": 0.85
}
```

**Пример с curl:**
```bash
curl -X POST "http://localhost:8000/heart-prediction/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "age": 45,
    "sex": 1,
    "cp": 1,
    "trestbps": 130,
    "chol": 250,
    "fbs": 0,
    "restecg": 0,
    "thalach": 150,
    "exang": 0,
    "oldpeak": 2.0,
    "slope": 1,
    "ca": 0,
    "thal": 1,
    "pulse": 85
  }'
```

#### Проверка здоровья ML сервиса

**Endpoint:** `GET /heart-prediction/health`

**Описание:** Проверяет состояние ML модели и сервиса.

**Ответ:**
```json
{
  "status": "healthy",
  "model_info": {
    "model_path": "data/processed/model.pkl",
    "model_type": "RandomForestClassifier",
    "features_count": 25,
    "is_loaded": true,
    "is_healthy": true
  }
}
```

#### Получить важность признаков

**Endpoint:** `GET /heart-prediction/feature-importance`

**Описание:** Возвращает важность признаков для ML модели.

**Ответ:**
```json
{
  "feature_importance": {
    "age": 0.15,
    "thalach": 0.12,
    "cp": 0.10,
    "oldpeak": 0.08
  },
  "top_features": [
    ["age", 0.15],
    ["thalach", 0.12],
    ["cp", 0.10]
  ]
}
```

## Примеры использования

### Python

```python
import requests

# Базовый URL
BASE_URL = "http://localhost:8000"

# Пример запроса к кардио-ассистенту
def get_cardio_analysis(age, pulse, risk, symptoms):
    url = f"{BASE_URL}/cardio-assistant/"
    data = {
        "age": age,
        "pulse": pulse,
        "risk": risk,
        "symptoms": symptoms
    }
    
    response = requests.post(url, json=data)
    return response.json()

# Пример запроса для предсказания риска
def predict_heart_risk(patient_data):
    url = f"{BASE_URL}/heart-prediction/predict"
    response = requests.post(url, json=patient_data)
    return response.json()

# Использование
if __name__ == "__main__":
    # Анализ от кардио-ассистента
    analysis = get_cardio_analysis(
        age=45,
        pulse=85,
        risk="средний",
        symptoms="одышка при физической нагрузке"
    )
    print("Анализ:", analysis["response"])
    
    # Предсказание риска
    patient_data = {
        "age": 45,
        "sex": 1,
        "cp": 1,
        "trestbps": 130,
        "chol": 250,
        "fbs": 0,
        "restecg": 0,
        "thalach": 150,
        "exang": 0,
        "oldpeak": 2.0,
        "slope": 1,
        "ca": 0,
        "thal": 1,
        "pulse": 85
    }
    
    prediction = predict_heart_risk(patient_data)
    print(f"Риск: {prediction['risk']}, Вероятность: {prediction['probability']}")
```

### JavaScript/Node.js

```javascript
const axios = require('axios');

const BASE_URL = 'http://localhost:8000';

// Функция для получения анализа от кардио-ассистента
async function getCardioAnalysis(age, pulse, risk, symptoms) {
    try {
        const response = await axios.post(`${BASE_URL}/cardio-assistant/`, {
            age,
            pulse,
            risk,
            symptoms
        });
        return response.data;
    } catch (error) {
        console.error('Ошибка:', error.response?.data || error.message);
        throw error;
    }
}

// Функция для предсказания риска
async function predictHeartRisk(patientData) {
    try {
        const response = await axios.post(`${BASE_URL}/heart-prediction/predict`, patientData);
        return response.data;
    } catch (error) {
        console.error('Ошибка:', error.response?.data || error.message);
        throw error;
    }
}

// Использование
async function main() {
    try {
        // Анализ от кардио-ассистента
        const analysis = await getCardioAnalysis(
            45,
            85,
            'средний',
            'одышка при физической нагрузке'
        );
        console.log('Анализ:', analysis.response);
        
        // Предсказание риска
        const patientData = {
            age: 45,
            sex: 1,
            cp: 1,
            trestbps: 130,
            chol: 250,
            fbs: 0,
            restecg: 0,
            thalach: 150,
            exang: 0,
            oldpeak: 2.0,
            slope: 1,
            ca: 0,
            thal: 1,
            pulse: 85
        };
        
        const prediction = await predictHeartRisk(patientData);
        console.log(`Риск: ${prediction.risk}, Вероятность: ${prediction.probability}`);
        
    } catch (error) {
        console.error('Ошибка выполнения:', error);
    }
}

main();
```

## Обработка ошибок

### HTTP статус коды

- `200` - Успешный запрос
- `422` - Ошибка валидации данных
- `429` - Превышен лимит запросов
- `500` - Внутренняя ошибка сервера

### Примеры ошибок

**Ошибка валидации:**
```json
{
  "detail": [
    {
      "loc": ["body", "age"],
      "msg": "ensure this value is less than or equal to 120",
      "type": "value_error.number.not_le"
    }
  ]
}
```

**Rate limiting:**
```json
{
  "detail": "Слишком много запросов. Попробуйте позже."
}
```

**Ошибка сервиса:**
```json
{
  "detail": "Ошибка AI сервиса: Invalid API key"
}
```

## Кеширование

API автоматически кеширует ответы для одинаковых запросов:

- **TTL:** 5 минут (300 секунд)
- **Ключ кеша:** MD5 хеш от всех параметров запроса
- **Флаг `cached`:** показывает, был ли ответ получен из кеша

## Rate Limiting

- **Лимит:** 5 запросов в минуту с одного IP
- **Окно:** скользящее окно в 60 секунд
- **Ошибка:** HTTP 429 при превышении лимита

## Swagger UI

Интерактивная документация доступна по адресу:
```
http://localhost:8000/docs
```

Здесь можно:
- Просмотреть все endpoints
- Протестировать API интерактивно
- Увидеть схемы запросов и ответов
- Скачать OpenAPI спецификацию

## Мониторинг

### Health checks

Регулярно проверяйте состояние сервисов:

```bash
# Общий health check
curl http://localhost:8000/health

# Health check кардио-ассистента
curl http://localhost:8000/cardio-assistant/health

# Health check ML сервиса
curl http://localhost:8000/heart-prediction/health
```

### Логи

Логи приложения сохраняются в `logs/app.log`:

```bash
# Просмотр логов в реальном времени
tail -f logs/app.log

# Поиск ошибок
grep "ERROR" logs/app.log
```

## Безопасность

### API ключи

- Храните `GROQ_API_KEY` в переменных окружения
- Никогда не коммитьте `.env` файл в репозиторий
- Используйте разные ключи для разработки и продакшена

### Валидация данных

- Все входные данные автоматически валидируются
- Проверяются типы, диапазоны и обязательность полей
- Защита от инъекций и некорректных данных

### CORS

Настройте разрешенные домены в переменной `ALLOWED_ORIGINS`:

```env
ALLOWED_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
```

## Производительность

### Оптимизация запросов

- Используйте кеширование для повторяющихся запросов
- Не превышайте rate limiting
- Группируйте запросы где возможно

### Мониторинг

Следите за метриками производительности:

```bash
# Статистика кеша
curl http://localhost:8000/cardio-assistant/health | jq '.cache_stats'

# Статистика rate limiting
curl http://localhost:8000/cardio-assistant/health | jq '.rate_limiter_stats'
```
