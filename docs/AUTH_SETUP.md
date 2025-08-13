# Настройка системы авторизации Smart Cardiologist

## Обзор

Система авторизации включает в себя:
- Регистрацию пользователей с подтверждением по email
- Аутентификацию по JWT токенам
- Защиту API маршрутов
- Сохранение истории анализов пользователей

## Требования

- Python 3.8+
- PostgreSQL 12+
- SMTP сервер для отправки email (Gmail, SendGrid и т.д.)

## Установка зависимостей

```bash
pip install -r requirements.txt
```

## Настройка базы данных

### 1. Установка PostgreSQL

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

**Arch Linux:**
```bash
sudo pacman -S postgresql
```

**macOS:**
```bash
brew install postgresql
```

### 2. Запуск PostgreSQL

```bash
# Ubuntu/Debian
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Arch Linux
sudo systemctl start postgresql
sudo systemctl enable postgresql

# macOS
brew services start postgresql
```

### 3. Настройка базы данных

```bash
# Создание пользователя и базы данных
sudo -u postgres psql

postgres=# CREATE USER myuser WITH PASSWORD 'mypassword';
postgres=# CREATE DATABASE mydb OWNER myuser;
postgres=# GRANT ALL PRIVILEGES ON DATABASE mydb TO myuser;
postgres=# \q
```

Или используйте автоматический скрипт:
```bash
python scripts/setup_database.py
```

### 4. Создание таблиц

```bash
# Инициализация Alembic
alembic init migrations

# Создание первой миграции
alembic revision --autogenerate -m "Initial migration"

# Применение миграции
alembic upgrade head
```

## Настройка переменных окружения

Создайте файл `.env` на основе `env.example`:

```bash
cp env.example .env
```

Отредактируйте `.env` файл:

```env
# База данных PostgreSQL
DB_HOST=localhost
DB_PORT=5432
DB_NAME=mydb
DB_USER=myuser
DB_PASSWORD=mypassword

# JWT настройки
SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Email настройки (Gmail)
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_FROM=your-email@gmail.com
MAIL_PORT=587
MAIL_SERVER=smtp.gmail.com
MAIL_TLS=true
MAIL_SSL=false

# AI Service
GROQ_API_KEY=your-groq-api-key

# Настройки активации
ACTIVATION_CODE_EXPIRE_MINUTES=10
MAX_ACTIVATION_ATTEMPTS=5

# Режим разработки
DEBUG=true
```

### Настройка Gmail для отправки email

1. Включите двухфакторную аутентификацию в Google аккаунте
2. Создайте пароль приложения:
   - Перейдите в настройки безопасности
   - Выберите "Пароли приложений"
   - Создайте новый пароль для "Почта"
3. Используйте этот пароль в `MAIL_PASSWORD`

## Запуск приложения

### 1. Проверка настроек

```bash
# Проверка подключения к базе данных
python -c "from src.services.database import check_db_connection; import asyncio; print(asyncio.run(check_db_connection()))"

# Проверка email сервиса
python -c "from src.services.email_service import EmailService; import asyncio; print(asyncio.run(EmailService().test_connection()))"
```

### 2. Запуск сервера

```bash
# Разработка
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Продакшен
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

## API Endpoints

### Авторизация

- `POST /api/v1/auth/register` - Регистрация пользователя
- `POST /api/v1/auth/activate` - Активация аккаунта
- `POST /api/v1/auth/login` - Вход в систему
- `POST /api/v1/auth/resend-activation` - Повторная отправка кода
- `GET /api/v1/auth/me` - Информация о пользователе
- `POST /api/v1/auth/logout` - Выход из системы

### Кардио-ассистент (требует авторизации)

- `POST /api/v1/cardio-assistant/` - Получить анализ от AI
- `GET /api/v1/cardio-assistant/history` - История анализов
- `GET /api/v1/cardio-assistant/history/{id}` - Детали анализа

## Примеры использования

### 1. Регистрация пользователя

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123"
  }'
```

### 2. Активация аккаунта

```bash
curl -X POST "http://localhost:8000/api/v1/auth/activate" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "activation_code": "123456"
  }'
```

### 3. Вход в систему

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123"
  }'
```

### 4. Использование защищенного API

```bash
# Получение анализа (требует токен)
curl -X POST "http://localhost:8000/api/v1/cardio-assistant/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "age": 45,
    "pulse": 85,
    "risk": "средний",
    "symptoms": "одышка при физической нагрузке"
  }'

# Получение истории анализов
curl -X GET "http://localhost:8000/api/v1/cardio-assistant/history" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Безопасность

### JWT токены
- Токены имеют ограниченное время жизни (30 минут по умолчанию)
- Используется алгоритм HS256 для подписи
- Секретный ключ должен быть изменен в продакшене

### Пароли
- Хэшируются с использованием bcrypt
- Минимальная длина: 8 символов
- Автоматическая генерация соли

### Активация
- 6-значные коды активации
- Время жизни: 10 минут
- Лимит попыток: 5 раз

### Rate Limiting
- Ограничение запросов по IP адресу
- Настраивается в `src/utils/rate_limiter.py`

## Мониторинг и логирование

### Логи
- Все операции логируются в консоль
- Уровень логирования: INFO
- Формат: `timestamp - module - level - message`

### Health Check
```bash
curl http://localhost:8000/health
```

### Конфигурация (только в режиме разработки)
```bash
curl http://localhost:8000/config
```

## Устранение неполадок

### Проблемы с базой данных
1. Проверьте, что PostgreSQL запущен
2. Убедитесь в правильности учетных данных
3. Проверьте права доступа пользователя

### Проблемы с email
1. Проверьте настройки SMTP
2. Убедитесь в правильности пароля приложения Gmail
3. Проверьте настройки безопасности Google аккаунта

### Проблемы с JWT
1. Проверьте SECRET_KEY в .env
2. Убедитесь в правильности алгоритма
3. Проверьте время жизни токена

## Развертывание в продакшене

1. Измените SECRET_KEY на уникальный
2. Настройте HTTPS
3. Ограничьте CORS origins
4. Настройте логирование в файлы
5. Используйте переменные окружения для секретов
6. Настройте мониторинг и алерты
7. Регулярно обновляйте зависимости
