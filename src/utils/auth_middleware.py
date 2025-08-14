from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.services.database import get_db
from src.services.auth_service import AuthService
from src.models.database import User
from src.models.auth_schemas import TokenData
import logging

logger = logging.getLogger(__name__)

# Схема безопасности для JWT токенов
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Получить текущего пользователя по JWT токену
    
    Args:
        credentials: JWT токен из заголовка Authorization
        db: Сессия базы данных
        
    Returns:
        User: Объект пользователя
        
    Raises:
        HTTPException: Если токен недействителен или пользователь не найден
    """
    try:
        # Проверяем токен
        token_data = AuthService.verify_token(credentials.credentials)
        if token_data is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Недействительный токен авторизации",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Получаем пользователя из базы данных
        user = await db.execute(
            select(User).where(User.id == token_data.user_id)
        )
        user = user.scalar_one_or_none()
        
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Пользователь не найден",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Проверяем, что аккаунт активирован
        if not user.is_activated:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Аккаунт не активирован"
            )
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_current_user: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Ошибка авторизации",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Получить текущего активного пользователя
    
    Args:
        current_user: Текущий пользователь
        
    Returns:
        User: Активный пользователь
    """
    # Дополнительные проверки можно добавить здесь
    # Например, проверка на блокировку аккаунта
    return current_user


def require_auth(func):
    """
    Декоратор для маршрутов, требующих авторизации
    
    Args:
        func: Функция маршрута
        
    Returns:
        Функция с зависимостью авторизации
    """
    # Этот декоратор можно использовать для дополнительной логики
    # В FastAPI авторизация обычно проверяется через Depends(get_current_user)
    return func
