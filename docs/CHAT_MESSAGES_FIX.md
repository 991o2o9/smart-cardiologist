# Исправление проблемы с сохранением сообщений в чате

## Проблема

После переписки с ИИ ассистентом и выхода из системы, данные о сообщениях в чате не сохранялись. При обращении к эндпоинту `/cardio-assistant/active` возвращался пустой массив `messages`, хотя сообщения были отправлены и должны были сохраниться в истории чатов.

### Симптомы:
- Эндпоинт `/cardio-assistant/active` возвращал `messages: []`
- Сообщения не отображались после перезагрузки страницы
- Данные о переписке терялись при выходе из системы

### Пример ответа с проблемой:
```json
{
  "id": 2,
  "messages": [],
  "summary": "Новый чат создан. Задайте ваш вопрос о здоровье сердца.",
  "created_at": "2025-08-22T14:35:12.464629Z",
  "updated_at": "2025-08-22T14:36:33.069034Z"
}
```

## Причина

Проблема была связана с тем, что SQLAlchemy не отслеживает изменения в JSONB полях PostgreSQL автоматически. При добавлении элементов в список `messages` через `append()`, SQLAlchemy не понимал, что поле было изменено, и не сохранял изменения в базе данных.

### Техническая причина:
- Поле `messages` в таблице `cardio_chats` имеет тип `JSONB`
- SQLAlchemy не отслеживает мутации в JSONB полях
- После `commit()` изменения терялись, так как SQLAlchemy считал объект неизмененным

## Решение

Добавлено явное уведомление SQLAlchemy об изменениях в JSONB поле с помощью функции `flag_modified()`.

### Изменения в коде:

#### 1. Файл: `src/api/cardio_assistant.py`

В функции `medical_chat()` добавлен вызов `flag_modified()`:

```python
# 7. Add messages to chat
now = datetime.datetime.utcnow().isoformat() + "Z"

# Добавляем сообщения пользователя
for message in data.messages:
    active_chat.messages.append({
        "role": message.role,
        "content": message.content,
        "timestamp": now
    })

# Добавляем ответ ИИ
active_chat.messages.append({
    "role": "assistant",
    "content": ai_response,
    "timestamp": now
})

# Обновляем summary
if not active_chat.summary and data.messages:
    active_chat.summary = data.messages[0].content[:100]

# Обновляем время
active_chat.updated_at = datetime.datetime.utcnow()

# Явно уведомляем SQLAlchemy об изменениях в JSONB поле
from sqlalchemy.orm.attributes import flag_modified
flag_modified(active_chat, "messages")

await db.commit()
```

#### 2. Улучшен summary для новых чатов

В функциях `get_or_create_active_chat()` и `create_new_chat()` изменен summary:

```python
new_chat = CardioChat(
    user_id=user.id,
    messages=[],
    summary="Новый чат создан. Задайте ваш вопрос о здоровье сердца.",
    is_active=True
)
```

## Результат

После внесения изменений:

### ✅ Проблема решена:
- Сообщения корректно сохраняются в базе данных
- Эндпоинт `/cardio-assistant/active` возвращает полную историю сообщений
- Данные сохраняются после перезагрузки страницы и выхода из системы

### Пример корректного ответа:
```json
{
  "chat_id": 2,
  "messages": [
    {
      "role": "user",
      "content": "У меня болит сердце, что делать?",
      "timestamp": "2025-08-22T20:44:51.586745Z"
    },
    {
      "role": "assistant", 
      "content": "Как кардиолог, я рекомендую вам обратиться к врачу для обследования.",
      "timestamp": "2025-08-22T20:44:51.586745Z"
    }
  ],
  "summary": "Новый чат создан. Задайте ваш вопрос о здоровье сердца.",
  "created_at": "2025-08-22T14:35:12.464629Z",
  "updated_at": "2025-08-22T20:44:51.408824Z"
}
```

## Тестирование

Созданы тестовые скрипты для проверки:
- Сохранения сообщений в JSONB поле
- Корректной работы эндпоинта `/active`
- Полной функциональности чата

Все тесты прошли успешно.

## Рекомендации

1. **Для JSONB полей**: Всегда используйте `flag_modified()` при изменении содержимого JSONB полей
2. **Для отладки**: Проверяйте `db.is_modified(obj)` для понимания, отслеживает ли SQLAlchemy изменения
3. **Для тестирования**: Создавайте тесты, которые проверяют сохранение данных через новые запросы к базе

## Связанные файлы

- `src/api/cardio_assistant.py` - основной код с исправлениями
- `src/models/database.py` - модель CardioChat с JSONB полем
- `src/models/schemas.py` - схемы данных для API
