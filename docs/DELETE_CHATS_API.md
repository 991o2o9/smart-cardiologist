# API для удаления чатов

## Обзор

Добавлены новые эндпоинты для управления историей чатов - удаление отдельных чатов и всей истории чатов.

## Новые эндпоинты

### 1. Удалить конкретный чат

**DELETE** `/cardio-assistant/history/{chat_id}`

Удаляет конкретный чат из истории. Активный чат не может быть удален.

**Параметры:**
- `chat_id` (int) - ID чата для удаления

**Заголовки:**
```
Authorization: Bearer {access_token}
```

**Ответ:**
```json
{
  "message": "Чат успешно удален"
}
```

**Ошибки:**
- `404` - Чат не найден
- `400` - Нельзя удалить активный чат

### 2. Удалить всю историю чатов

**DELETE** `/cardio-assistant/history`

Удаляет всю историю чатов пользователя. Активный чат не удаляется, но его сообщения очищаются.

**Заголовки:**
```
Authorization: Bearer {access_token}
```

**Ответ:**
```json
{
  "message": "Вся история чатов успешно удалена",
  "deleted_count": 3
}
```

## Логика работы

### Удаление конкретного чата:
1. Проверяется, что чат принадлежит пользователю
2. Проверяется, что чат не является активным
3. Чат удаляется из базы данных
4. Возвращается подтверждение удаления

### Удаление всей истории:
1. Получаются все чаты пользователя
2. Неактивные чаты удаляются
3. Активный чат очищается (сообщения удаляются, summary обновляется)
4. Возвращается количество удаленных чатов

## Безопасность

- Пользователь может удалять только свои чаты
- Активный чат защищен от удаления
- Все операции требуют авторизации

## Примеры использования

### Удаление конкретного чата:
```bash
curl -X DELETE "http://localhost:8000/cardio-assistant/history/123" \
  -H "Authorization: Bearer your_token_here"
```

### Удаление всей истории:
```bash
curl -X DELETE "http://localhost:8000/cardio-assistant/history" \
  -H "Authorization: Bearer your_token_here"
```

## Схемы данных

### DeleteChatResponse
```python
class DeleteChatResponse(BaseModel):
    message: str = "Чат успешно удален"
```

### DeleteAllChatsResponse
```python
class DeleteAllChatsResponse(BaseModel):
    message: str = "Вся история чатов успешно удалена"
    deleted_count: int
```

## Обработка ошибок

### 404 - Чат не найден
```json
{
  "detail": "Chat not found"
}
```

### 400 - Нельзя удалить активный чат
```json
{
  "detail": "Cannot delete active chat. Please activate another chat first."
}
```

### 401 - Не авторизован
```json
{
  "detail": "Not authenticated"
}
```

## Тестирование

Создан тестовый скрипт `scripts/test_delete_chats.py` который проверяет:
- ✅ Создание тестовых чатов
- ✅ Удаление конкретного чата
- ✅ Удаление всей истории
- ✅ Очистку активного чата
- ✅ Корректность финального состояния

## Использование на фронтенде

### Удаление конкретного чата:
```javascript
const response = await fetch(`/cardio-assistant/history/${chatId}`, {
  method: 'DELETE',
  headers: {
    'Authorization': `Bearer ${token}`
  }
});

if (response.ok) {
  const result = await response.json();
  console.log(result.message);
  // Обновить список чатов
} else {
  const error = await response.json();
  console.error(error.detail);
}
```

### Удаление всей истории:
```javascript
const response = await fetch('/cardio-assistant/history', {
  method: 'DELETE',
  headers: {
    'Authorization': `Bearer ${token}`
  }
});

if (response.ok) {
  const result = await response.json();
  console.log(`${result.message}. Удалено чатов: ${result.deleted_count}`);
  // Очистить интерфейс
} else {
  const error = await response.json();
  console.error(error.detail);
}
```

## Связанные файлы

- `src/api/cardio_assistant.py` - эндпоинты удаления
- `src/models/schemas.py` - схемы ответов
- `scripts/test_delete_chats.py` - тестовый скрипт
