# API для активного чата

## Обзор

Система активного чата позволяет пользователям вести непрерывные диалоги с ИИ-кардиологом. Каждый пользователь имеет один активный чат, в который добавляются все новые сообщения.

## Новые эндпоинты

### 1. Получить активный чат

**GET** `/cardio-assistant/active`

Получает текущий активный чат пользователя. Если активного чата нет, создает новый.

**Заголовки:**
```
Authorization: Bearer {access_token}
```

**Ответ:**
```json
{
  "chat_id": 123,
  "messages": [
    {
      "role": "user",
      "content": "У меня болит сердце",
      "timestamp": "2024-01-15T10:30:00Z"
    },
    {
      "role": "assistant",
      "content": "Как кардиолог, я рекомендую...",
      "timestamp": "2024-01-15T10:30:05Z"
    }
  ],
  "summary": "У меня болит сердце...",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:35:00Z"
}
```

### 2. Создать новый чат

**POST** `/cardio-assistant/create`

Создает новый чат и делает его активным. Предыдущий активный чат становится неактивным.

**Заголовки:**
```
Authorization: Bearer {access_token}
```

**Ответ:**
```json
{
  "chat_id": 124,
  "message": "Новый чат создан"
}
```

### 3. Активировать существующий чат

**POST** `/cardio-assistant/history/{chat_id}/activate`

Активирует конкретный чат из истории. Все остальные чаты становятся неактивными.

**Параметры:**
- `chat_id` (int) - ID чата для активации

**Заголовки:**
```
Authorization: Bearer {access_token}
```

**Ответ:**
```json
{
  "message": "Chat activated successfully"
}
```

## Обновленные эндпоинты

### Отправка сообщения

**POST** `/cardio-assistant/`

Теперь добавляет сообщения в активный чат пользователя вместо создания нового чата.

**Тело запроса:**
```json
{
  "messages": [
    {
      "role": "user",
      "content": "У меня болит сердце"
    }
  ]
}
```

**Ответ:**
```json
{
  "response": "Как кардиолог, я рекомендую..."
}
```

## Логика работы

### При первом обращении:
1. Пользователь вызывает `GET /cardio-assistant/active`
2. Система создает новый чат и делает его активным
3. Возвращает пустой чат с `chat_id`

### При отправке сообщения:
1. Пользователь отправляет `POST /cardio-assistant/`
2. Система находит активный чат пользователя
3. Добавляет сообщение пользователя и ответ ИИ в активный чат
4. Возвращает только ответ ИИ

### При перезагрузке страницы:
1. Фронтенд вызывает `GET /cardio-assistant/active`
2. Система возвращает активный чат со всей историей
3. Фронтенд отображает все сообщения

## Структура данных

### Пользователь (User)
```sql
active_chat_id INTEGER REFERENCES cardio_chats(id)
```

### Чат (CardioChat)
```sql
is_active BOOLEAN DEFAULT true
```

## Примеры использования

### Инициализация чата на фронтенде:
```javascript
// При загрузке страницы
const response = await fetch('/cardio-assistant/active', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
const activeChat = await response.json();

// Сохраняем chat_id в localStorage
localStorage.setItem('activeChatId', activeChat.chat_id);

// Отображаем сообщения
displayMessages(activeChat.messages);
```

### Отправка сообщения:
```javascript
// Отправляем сообщение
const response = await fetch('/cardio-assistant/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    messages: [{ role: 'user', content: message }]
  })
});

const result = await response.json();
// Добавляем ответ в интерфейс
addMessage('assistant', result.response);
```

### Создание нового чата:
```javascript
// Создаем новый чат
const response = await fetch('/cardio-assistant/create', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`
  }
});

const result = await response.json();
// Обновляем chat_id в localStorage
localStorage.setItem('activeChatId', result.chat_id);
// Очищаем интерфейс
clearMessages();
```

## Обработка ошибок

### 404 - Чат не найден
```json
{
  "detail": "Chat not found"
}
```

### 401 - Не авторизован
```json
{
  "detail": "Not authenticated"
}
```

### 500 - Ошибка сервера
```json
{
  "detail": "AI service error: ..."
}
```

## Миграция

Для применения изменений выполните:

```bash
python scripts/apply_active_chat_migration.py
```

Это добавит необходимые поля в базу данных:
- `active_chat_id` в таблицу `users`
- `is_active` в таблицу `cardio_chats`
