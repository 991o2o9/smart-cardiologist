# Исправление проблем с аутентификацией на Cloud Run

## Проблема

На Cloud Run пользователи теряют сессию и получают 401 ошибку при повторном входе через некоторое время.

## Причины проблемы

1. **Stateless архитектура Cloud Run** - каждый запрос может обрабатываться разными экземплярами
2. **Неправильная логика refresh token** - создавался новый refresh token при каждом обновлении
3. **Проблемы с CORS настройками** - не все заголовки были разрешены
4. **Отсутствие автоматического обновления токенов** на клиентской стороне

## Исправления на серверной стороне

### 1. Исправлена логика refresh token

**Проблема:** При каждом обновлении создавался новый refresh token
**Решение:** Теперь refresh token остается тем же, обновляется только access token

```python
# В src/services/auth_service.py
async def refresh_access_token(cls, db: AsyncSession, refresh_token: str) -> dict:
    # ... проверка токена ...
    
    # Создаем только новый access token
    new_access_token = cls.create_access_token(
        data={"sub": user.email, "user_id": user.id},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": new_access_token,
        "refresh_token": refresh_token,  # Возвращаем тот же refresh token
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        "refresh_expires_in": settings.REFRESH_TOKEN_EXPIRE_DAYS
    }
```

### 2. Улучшены CORS настройки

**Проблема:** Не все заголовки были разрешены для Cloud Run
**Решение:** Добавлены все необходимые заголовки

```python
# В src/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,  # Всегда разрешаем credentials
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=[
        "Accept", "Accept-Language", "Content-Language", "Content-Type",
        "Authorization", "X-Requested-With", "Origin",
        "Access-Control-Request-Method", "Access-Control-Request-Headers",
        "Cache-Control", "Pragma"
    ],
    expose_headers=["Content-Length", "Content-Range", "X-Total-Count"],
    max_age=86400,  # 24 часа
)
```

### 3. Добавлен endpoint для проверки токена

```python
# В src/api/auth.py
@router.post("/verify", response_model=dict)
async def verify_token(current_user: User = Depends(get_current_user)):
    """Проверка валидности токена без его обновления"""
    return {
        "valid": True,
        "user": {
            "id": current_user.id,
            "email": current_user.email,
            "is_activated": current_user.is_activated
        }
    }
```

## Рекомендации для клиентской стороны

### 1. Хранение токенов

```javascript
// Рекомендуется хранить refresh token в httpOnly cookie
// Access token можно хранить в localStorage или sessionStorage

class TokenManager {
    constructor() {
        this.accessToken = localStorage.getItem('accessToken');
        this.refreshToken = this.getRefreshTokenFromCookie();
    }

    setAccessToken(token) {
        this.accessToken = token;
        localStorage.setItem('accessToken', token);
    }

    setRefreshToken(token) {
        this.refreshToken = token;
        // Устанавливаем httpOnly cookie через сервер
        this.setRefreshTokenCookie(token);
    }

    getRefreshTokenFromCookie() {
        // Получаем из cookie (если доступно)
        return document.cookie
            .split('; ')
            .find(row => row.startsWith('refreshToken='))
            ?.split('=')[1];
    }

    setRefreshTokenCookie(token) {
        // Устанавливаем cookie через API
        fetch('/auth/set-refresh-cookie', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ refresh_token: token })
        });
    }
}
```

### 2. Автоматическое обновление токенов

```javascript
class ApiClient {
    constructor() {
        this.tokenManager = new TokenManager();
        this.baseURL = 'https://your-cloud-run-url.com';
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        
        // Добавляем токен к запросу
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };

        if (this.tokenManager.accessToken) {
            headers['Authorization'] = `Bearer ${this.tokenManager.accessToken}`;
        }

        try {
            const response = await fetch(url, {
                ...options,
                headers,
                credentials: 'include' // Важно для cookies
            });

            // Если получили 401, пробуем обновить токен
            if (response.status === 401) {
                const refreshed = await this.refreshToken();
                if (refreshed) {
                    // Повторяем запрос с новым токеном
                    headers['Authorization'] = `Bearer ${this.tokenManager.accessToken}`;
                    return fetch(url, {
                        ...options,
                        headers,
                        credentials: 'include'
                    });
                } else {
                    // Refresh token истек, нужно перелогиниться
                    this.logout();
                    throw new Error('Authentication required');
                }
            }

            return response;
        } catch (error) {
            console.error('API request error:', error);
            throw error;
        }
    }

    async refreshToken() {
        try {
            const response = await fetch(`${this.baseURL}/auth/refresh`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    refresh_token: this.tokenManager.refreshToken
                }),
                credentials: 'include'
            });

            if (response.ok) {
                const data = await response.json();
                this.tokenManager.setAccessToken(data.access_token);
                this.tokenManager.setRefreshToken(data.refresh_token);
                return true;
            } else {
                return false;
            }
        } catch (error) {
            console.error('Token refresh failed:', error);
            return false;
        }
    }

    async verifyToken() {
        try {
            const response = await this.request('/auth/verify', {
                method: 'POST'
            });
            return response.ok;
        } catch (error) {
            return false;
        }
    }

    logout() {
        this.tokenManager.accessToken = null;
        localStorage.removeItem('accessToken');
        // Очищаем cookie через API
        fetch(`${this.baseURL}/auth/logout`, {
            method: 'POST',
            credentials: 'include'
        });
    }
}
```

### 3. Интерцептор для автоматического обновления

```javascript
// Создаем глобальный API клиент
const apiClient = new ApiClient();

// Интерцептор для всех API запросов
async function apiRequest(endpoint, options = {}) {
    return apiClient.request(endpoint, options);
}

// Пример использования
async function getUserProfile() {
    try {
        const response = await apiRequest('/auth/me');
        if (response.ok) {
            return await response.json();
        }
    } catch (error) {
        console.error('Failed to get user profile:', error);
    }
}
```

### 4. Проверка токена при загрузке приложения

```javascript
// При загрузке приложения
async function initializeApp() {
    // Проверяем, есть ли сохраненный токен
    if (apiClient.tokenManager.accessToken) {
        // Проверяем валидность токена
        const isValid = await apiClient.verifyToken();
        if (!isValid) {
            // Пробуем обновить токен
            const refreshed = await apiClient.refreshToken();
            if (!refreshed) {
                // Нужно перелогиниться
                redirectToLogin();
                return;
            }
        }
    } else {
        // Нет токена, нужно войти
        redirectToLogin();
        return;
    }

    // Токен валиден, загружаем приложение
    loadApp();
}
```

## Тестирование

Запустите тест для проверки исправлений:

```bash
# Локальное тестирование
python scripts/test_cloud_run_auth.py

# Тестирование на Cloud Run
python scripts/test_cloud_run_auth.py https://your-cloud-run-url.com
```

## Дополнительные рекомендации

### 1. Настройки Cloud Run

Убедитесь, что в Cloud Run настроены правильные переменные окружения:

```yaml
# В cloudbuild.yaml
- --update-env-vars
- >
  ACCESS_TOKEN_EXPIRE_MINUTES=30,
  REFRESH_TOKEN_EXPIRE_DAYS=30,
  ALLOW_CREDENTIALS=true,
  ALLOWED_ORIGINS=https://your-frontend-domain.com
```

### 2. Мониторинг

Добавьте логирование для отслеживания проблем с аутентификацией:

```python
# В src/services/auth_service.py
logger.info(f"Token refresh requested for user: {user.email}")
logger.warning(f"Invalid refresh token for user: {user.email}")
```

### 3. Безопасность

- Используйте HTTPS для всех запросов
- Регулярно меняйте SECRET_KEY в продакшене
- Ограничивайте количество попыток обновления токена
- Логируйте подозрительную активность

## Проверка исправлений

После внедрения исправлений проверьте:

1. ✅ Пользователи остаются залогиненными после перезапуска Cloud Run
2. ✅ Refresh token работает корректно
3. ✅ CORS не блокирует запросы с фронтенда
4. ✅ Автоматическое обновление токенов работает
5. ✅ Выход из системы корректно очищает токены
