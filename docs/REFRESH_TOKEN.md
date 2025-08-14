# Refresh Token Система

## Обзор

Система refresh token была добавлена для обеспечения длительной авторизации пользователей и улучшения безопасности приложения.

## Основные возможности

### 1. Refresh Token Аутентификация

- **Access Token**: Короткоживущий токен (30 минут) для доступа к API
- **Refresh Token**: Долгоживущий токен (30 дней) для обновления access token
- **Автоматическое обновление**: Пользователи могут оставаться залогиненными без повторного ввода пароля

### 2. Шифрование медицинских данных

- **End-to-end шифрование**: Все медицинские данные пользователей шифруются перед сохранением в базу данных
- **Безопасное хранение**: Данные расшифровываются только при запросе авторизованным пользователем
- **Защита конфиденциальности**: Даже администраторы базы данных не могут прочитать медицинские данные

## API Endpoints

### Аутентификация

#### POST /auth/login
Вход в систему с получением access и refresh токенов.

**Запрос:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Ответ:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 30,
  "refresh_expires_in": 30
}
```

#### POST /auth/refresh
Обновление access token с помощью refresh token.

**Запрос:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Ответ:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 30
}
```

#### POST /auth/logout
Выход из системы с инвалидацией refresh token.

**Заголовки:**
```
Authorization: Bearer <access_token>
```

**Ответ:**
```json
{
  "message": "Выход выполнен успешно",
  "success": true
}
```

### Защищенные Endpoints

Все медицинские endpoints теперь требуют авторизации:

#### POST /cardio-assistant/
Кардио-анализ с шифрованием данных.

**Заголовки:**
```
Authorization: Bearer <access_token>
```

**Запрос:**
```json
{
  "age": 45,
  "pulse": 85,
  "risk": "средний",
  "symptoms": "Боли в груди, одышка при физической нагрузке"
}
```

#### POST /heart-prediction/predict
Предсказание сердечных заболеваний с шифрованием данных.

**Заголовки:**
```
Authorization: Bearer <access_token>
```

**Запрос:**
```json
{
  "age": 55,
  "sex": 1,
  "cp": 2,
  "trestbps": 140,
  "chol": 250,
  "fbs": 1,
  "restecg": 1,
  "thalach": 150,
  "exang": 0,
  "oldpeak": 1.5,
  "slope": 1,
  "ca": 1,
  "thal": 2,
  "pulse": 80
}
```

## Безопасность

### Шифрование данных

Система использует Fernet шифрование для защиты медицинских данных:

- **Ключ шифрования**: Генерируется на основе SECRET_KEY
- **Алгоритм**: AES-128 в режиме CBC
- **Автоматическое шифрование**: Все медицинские данные шифруются перед сохранением
- **Автоматическая расшифровка**: Данные расшифровываются при запросе авторизованным пользователем

### Защищенные поля

Следующие поля автоматически шифруются:

- `symptoms` - симптомы пациента
- `ai_response` - ответ AI
- `risk` - уровень риска
- `risk_prediction` - предсказание риска
- `pulse` - пульс
- `age` - возраст
- `sex` - пол
- `cp` - тип боли в груди
- `trestbps` - систолическое давление
- `chol` - уровень холестерина
- `fbs` - уровень сахара в крови
- `restecg` - результаты ЭКГ
- `thalach` - максимальная частота сердечных сокращений
- `exang` - стенокардия при физической нагрузке
- `oldpeak` - депрессия ST
- `slope` - наклон сегмента ST
- `ca` - количество сосудов
- `thal` - талассемия
- `probability` - вероятность заболевания

## Настройки

### Конфигурация токенов

В `config/settings.py`:

```python
# JWT
ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
REFRESH_TOKEN_EXPIRE_DAYS: int = 30
```

### Конфигурация шифрования

Шифрование использует SECRET_KEY из настроек:

```python
SECRET_KEY: str = "your-secret-key-change-in-production"
```

## Миграция базы данных

Для добавления полей refresh token выполните:

```bash
# Создание миграции
alembic revision --autogenerate -m "Add refresh token fields to User model"

# Применение миграции
alembic upgrade head
```

## Тестирование

Для тестирования refresh token системы используйте:

```bash
python scripts/test_refresh_token.py
```

Этот скрипт проверит:
- Регистрацию и активацию пользователя
- Вход с получением токенов
- Обновление access token
- Доступ к защищенным endpoints
- Шифрование медицинских данных
- Выход из системы

## Рекомендации по использованию

### На клиентской стороне

1. **Хранение токенов**: Храните refresh token в безопасном месте (например, httpOnly cookie)
2. **Автоматическое обновление**: Реализуйте автоматическое обновление access token при получении 401 ошибки
3. **Обработка ошибок**: Обрабатывайте случаи истечения refresh token

### Пример клиентского кода

```javascript
// Функция для обновления токена
async function refreshAccessToken() {
  try {
    const response = await fetch('/auth/refresh', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        refresh_token: getRefreshToken()
      })
    });
    
    if (response.ok) {
      const data = await response.json();
      setAccessToken(data.access_token);
      return data.access_token;
    } else {
      // Refresh token истек, нужно перелогиниться
      logout();
    }
  } catch (error) {
    console.error('Error refreshing token:', error);
    logout();
  }
}

// Интерцептор для автоматического обновления токена
async function apiRequest(url, options = {}) {
  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        ...options.headers,
        'Authorization': `Bearer ${getAccessToken()}`
      }
    });
    
    if (response.status === 401) {
      // Токен истек, пробуем обновить
      const newToken = await refreshAccessToken();
      if (newToken) {
        // Повторяем запрос с новым токеном
        return fetch(url, {
          ...options,
          headers: {
            ...options.headers,
            'Authorization': `Bearer ${newToken}`
          }
        });
      }
    }
    
    return response;
  } catch (error) {
    console.error('API request error:', error);
    throw error;
  }
}
```

## Безопасность

### Рекомендации

1. **Регулярная смена SECRET_KEY**: Меняйте SECRET_KEY в продакшене
2. **HTTPS**: Используйте HTTPS для всех API запросов
3. **Валидация токенов**: Всегда проверяйте валидность токенов на сервере
4. **Логирование**: Ведите логи всех операций с токенами
5. **Мониторинг**: Отслеживайте подозрительную активность

### Угрозы и защита

- **XSS**: Используйте httpOnly cookies для refresh token
- **CSRF**: Используйте CSRF токены для критических операций
- **Token theft**: Ограничивайте время жизни токенов
- **Replay attacks**: Используйте nonce или timestamp в токенах
