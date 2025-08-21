# Реализация активного чата

## Что было сделано

### 1. Изменения в базе данных

#### Добавлены новые поля:
- **`active_chat_id`** в таблицу `users` - ID активного чата пользователя
- **`is_active`** в таблицу `cardio_chats` - флаг активности чата

#### Миграция:
- Создана миграция `003_add_active_chat_support.py`
- Добавлены внешние ключи и индексы

### 2. Обновленные модели

#### User модель:
```python
active_chat_id = Column(Integer, ForeignKey("cardio_chats.id"), nullable=True)
active_chat = relationship("CardioChat", foreign_keys=[active_chat_id])
```

#### CardioChat модель:
```python
is_active = Column(Boolean, default=True, nullable=False)
user = relationship("User", foreign_keys=[user_id])
```

### 3. Новые API эндпоинты

#### `GET /cardio-assistant/active`
- Получает активный чат пользователя
- Если активного чата нет - создает новый
- Возвращает полную историю сообщений

#### `POST /cardio-assistant/create`
- Создает новый чат
- Деактивирует предыдущий активный чат
- Возвращает ID нового чата

#### `POST /cardio-assistant/history/{chat_id}/activate`
- Активирует конкретный чат из истории
- Деактивирует все остальные чаты пользователя

### 4. Обновленная логика чата

#### Основные изменения:
- **Больше не создается новый чат при каждом сообщении**
- Сообщения добавляются в активный чат пользователя
- Поддерживается полная история диалога
- ИИ получает контекст всего разговора

#### Функции:
- `get_or_create_active_chat()` - получение/создание активного чата
- `deactivate_other_chats()` - деактивация других чатов
- Обновленная логика в `medical_chat()` эндпоинте

### 5. Новые схемы данных

```python
class ActiveChatResponse(BaseModel):
    chat_id: int
    messages: List[CardioChatMessage]
    summary: str
    created_at: str
    updated_at: str

class CreateChatResponse(BaseModel):
    chat_id: int
    message: str
```

## Как это работает

### При первом обращении пользователя:
1. Вызывается `GET /cardio-assistant/active`
2. Система создает новый чат и делает его активным
3. Возвращается пустой чат с `chat_id`

### При отправке сообщения:
1. Пользователь отправляет `POST /cardio-assistant/`
2. Система находит активный чат пользователя
3. Добавляет сообщение пользователя и ответ ИИ
4. ИИ получает полную историю диалога для контекста

### При перезагрузке страницы:
1. Фронтенд вызывает `GET /cardio-assistant/active`
2. Система возвращает активный чат со всей историей
3. Фронтенд отображает все сообщения

## Преимущества новой системы

### ✅ Решены все проблемы:
- **Уникальный chat_id** - каждый пользователь имеет активный чат
- **Сохранение chat_id** - хранится в базе данных
- **Автоматическое создание** - при первом обращении
- **Загрузка истории** - при перезагрузке страницы
- **Полная история** - все сообщения сохраняются

### ✅ Дополнительные возможности:
- **Контекст для ИИ** - получает всю историю диалога
- **Переключение между чатами** - можно активировать старые чаты
- **Создание новых чатов** - для новых тем разговора
- **Автоматическая деактивация** - только один активный чат

## Тестирование

Создан тестовый скрипт `scripts/test_active_chat.py` который проверяет:
- ✅ Структуру таблиц
- ✅ Создание пользователей и чатов
- ✅ Установку активного чата
- ✅ Добавление сообщений
- ✅ Сохранение активности

## Использование на фронтенде

### Инициализация:
```javascript
// При загрузке страницы
const response = await fetch('/cardio-assistant/active');
const activeChat = await response.json();
localStorage.setItem('activeChatId', activeChat.chat_id);
displayMessages(activeChat.messages);
```

### Отправка сообщения:
```javascript
// Отправляем сообщение
const response = await fetch('/cardio-assistant/', {
  method: 'POST',
  body: JSON.stringify({
    messages: [{ role: 'user', content: message }]
  })
});
const result = await response.json();
addMessage('assistant', result.response);
```

### Создание нового чата:
```javascript
// Создаем новый чат
const response = await fetch('/cardio-assistant/create', {
  method: 'POST'
});
const result = await response.json();
localStorage.setItem('activeChatId', result.chat_id);
clearMessages();
```

## Статус реализации

🎉 **Полностью реализовано и протестировано**

- ✅ База данных обновлена
- ✅ API эндпоинты работают
- ✅ Логика активного чата реализована
- ✅ Тесты проходят успешно
- ✅ Документация создана

Система готова к использованию на фронтенде!
