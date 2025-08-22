# AI Providers Configuration

Smart Cardiologist поддерживает два AI провайдера для генерации медицинских консультаций:

## 🚀 Поддерживаемые провайдеры

### 1. GROQ
- **Модель**: `openai/gpt-oss-20b`
- **Преимущества**: Быстрые ответы, высокая производительность
- **API**: Официальный Groq API

### 2. GPT (через AIMLAPI)
- **Модель**: `deepseek-chat`
- **Преимущества**: Продвинутые возможности, высокая точность
- **API**: AIMLAPI (альтернативный OpenAI API)

## ⚙️ Конфигурация

### Переменные окружения

Добавьте следующие переменные в ваш `.env` файл:

```env
# Выбор AI провайдера (GROQ или GPT)
AI_PROVIDER=GROQ

# API ключи для провайдеров
GROQ_API_KEY=your-groq-api-key-here
GPT_API_KEY=your-gpt-api-key-here
```

### Получение API ключей

#### GROQ API Key
1. Зарегистрируйтесь на [groq.com](https://groq.com)
2. Перейдите в раздел API Keys
3. Создайте новый API ключ
4. Скопируйте ключ в переменную `GROQ_API_KEY`

#### GPT API Key (AIMLAPI)
1. Зарегистрируйтесь на [aimlapi.com](https://aimlapi.com)
2. Получите API ключ
3. Скопируйте ключ в переменную `GPT_API_KEY`

## 🔄 Переключение между провайдерами

### Автоматическое переключение

Используйте скрипт для быстрого переключения:

```bash
# Переключиться на GROQ
python scripts/switch_ai_provider.py GROQ

# Переключиться на GPT
python scripts/switch_ai_provider.py GPT

# Проверить текущий провайдер
python scripts/switch_ai_provider.py status
```

### Ручное переключение

Измените переменную `AI_PROVIDER` в файле `.env`:

```env
AI_PROVIDER=GROQ  # или GPT
```

**Важно**: После изменения провайдера перезапустите приложение.

## 🧪 Тестирование

### Проверка конфигурации

```bash
python scripts/test_ai_config.py
```

### Полное тестирование AI сервиса

```bash
python scripts/test_ai_service.py
```

### Тестирование через API

#### Health Check
```bash
curl http://localhost:8000/health
```

**Ответ:**
```json
{
    "status": "healthy",
    "service": "Smart Cardiologist API",
    "version": "1.0.0",
    "database": "connected",
    "ai_service": {
        "provider": "GROQ",
        "status": "connected"
    },
    "timestamp": "2024-01-01T00:00:00Z"
}
```

#### Config Check
```bash
curl http://localhost:8000/config
```

**Ответ:**
```json
{
    "debug": true,
    "database_host": "localhost",
    "database_port": 5432,
    "database_name": "mydb",
    "rate_limit": 5,
    "cache_ttl": 300,
    "ai_provider": "GROQ",
    "ai_model": "openai/gpt-oss-20b",
    "allowed_origins": ["*"],
    "cors_all_origins_allowed": true,
    "cors_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    "cors_headers": ["*"],
    "cors_credentials": true,
    "cors_max_age": 600
}
```

## 📊 Логирование

При запуске приложения в логах отображается информация о выбранном AI провайдере:

```
2024-01-01 12:00:00 - src.services.ai_service - INFO - AI Service initialized with Groq provider
```

или

```
2024-01-01 12:00:00 - src.services.ai_service - INFO - AI Service initialized with GPT provider (AIMLAPI)
```

## 🔧 Устранение неполадок

### Ошибка "API key not found"
```
ValueError: GROQ_API_KEY not found in environment variables
```

**Решение**: Убедитесь, что API ключ правильно установлен в `.env` файле.

### Ошибка "Unsupported AI provider"
```
ValueError: Unsupported AI provider: INVALID. Use 'GROQ' or 'GPT'
```

**Решение**: Проверьте значение переменной `AI_PROVIDER` - должно быть `GROQ` или `GPT`.

### AI сервис показывает "disconnected"
Это может происходить при:
- Неправильном API ключе
- Проблемах с сетью
- Превышении лимитов API

**Решение**: 
1. Проверьте правильность API ключа
2. Убедитесь в наличии интернет-соединения
3. Проверьте лимиты API в личном кабинете провайдера

### Ошибка "unexpected keyword argument 'top_k'"
```
Error when contacting GPT AI: Completions.create() got an unexpected keyword argument 'top_k'
```

**Решение**: Эта ошибка исправлена в последней версии. Параметр `top_k` не поддерживается в OpenAI API и был удален из кода.

## 📈 Производительность

### GROQ
- **Скорость**: Очень высокая
- **Латентность**: ~100-200ms
- **Стоимость**: Низкая
- **Качество**: Хорошее

### GPT (AIMLAPI)
- **Скорость**: Высокая
- **Латентность**: ~200-500ms
- **Стоимость**: Средняя
- **Качество**: Отличное

## 🔒 Безопасность

- API ключи хранятся в переменных окружения
- Ключи не передаются в логах
- Поддерживается шифрование данных
- Все запросы к AI провайдерам логируются

## 📝 Примеры использования

### Cardio Analysis
```python
from src.services.ai_service import AIService

ai_service = AIService()

analysis = ai_service.get_cardio_analysis(
    age=45,
    pulse=85,
    risk="Medium",
    symptoms="Chest pain, shortness of breath"
)
```

### Health Advice
```python
advice = ai_service.get_health_advice(
    condition="High blood pressure"
)
```

### Provider Info
```python
info = ai_service.get_provider_info()
print(f"Provider: {info['provider']}")
print(f"Model: {info['model']}")
print(f"Healthy: {info['healthy']}")
```
