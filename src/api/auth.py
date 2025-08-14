from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.services.database import get_db
from src.services.auth_service import AuthService
from src.services.email_service import EmailService
from src.utils.auth_middleware import get_current_user
from src.models.auth_schemas import (
    UserRegister, UserLogin, ActivationCode, ResendActivation,
    Token, UserResponse, MessageResponse, RefreshToken
)
from src.models.database import User
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Авторизация"])

# Инициализация сервисов
email_service = EmailService()


@router.post("/register", response_model=MessageResponse)
async def register_user(
    user_data: UserRegister,
    db: AsyncSession = Depends(get_db)
):
    """
    Регистрация нового пользователя
    
    - **email**: Email пользователя
    - **password**: Пароль (минимум 8 символов)
    """
    try:
        # Регистрируем пользователя
        user = await AuthService.register_user(
            db=db,
            email=user_data.email,
            password=user_data.password
        )
        
        # Отправляем email с кодом активации
        activation_sent = await email_service.send_activation_email(
            email=user.email,
            activation_code=user.activation_code
        )
        
        if not activation_sent:
            logger.warning(f"Failed to send activation email to {user.email}")
            # Можно добавить логику повторной отправки или уведомления администратора
        
        return MessageResponse(
            message="Регистрация успешна! Проверьте email для получения кода активации.",
            success=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при регистрации пользователя"
        )


@router.post("/activate", response_model=MessageResponse)
async def activate_account(
    activation_data: ActivationCode,
    db: AsyncSession = Depends(get_db)
):
    """
    Активация аккаунта по коду
    
    - **email**: Email пользователя
    - **activation_code**: 6-значный код активации
    """
    try:
        # Активируем аккаунт
        success = await AuthService.activate_account(
            db=db,
            email=activation_data.email,
            activation_code=activation_data.activation_code
        )
        
        if success:
            # Отправляем приветственный email
            await email_service.send_welcome_email(activation_data.email)
            
            return MessageResponse(
                message="Аккаунт успешно активирован! Теперь вы можете войти в систему.",
                success=True
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ошибка при активации аккаунта"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Activation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при активации аккаунта"
        )


@router.post("/resend-activation", response_model=MessageResponse)
async def resend_activation_code(
    resend_data: ResendActivation,
    db: AsyncSession = Depends(get_db)
):
    """
    Повторная отправка кода активации
    
    - **email**: Email пользователя
    """
    try:
        # Генерируем новый код активации
        new_code = await AuthService.resend_activation_code(
            db=db,
            email=resend_data.email
        )
        
        # Отправляем новый код
        email_sent = await email_service.send_activation_email(
            email=resend_data.email,
            activation_code=new_code
        )
        
        if email_sent:
            return MessageResponse(
                message="Новый код активации отправлен на ваш email.",
                success=True
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка при отправке email"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Resend activation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при отправке кода активации"
        )


@router.post("/login", response_model=Token)
async def login_user(
    user_data: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """
    Вход в систему
    
    - **email**: Email пользователя
    - **password**: Пароль
    
    Возвращает access token и refresh token
    """
    try:
        # Выполняем вход
        token_data = await AuthService.login_user(
            db=db,
            email=user_data.email,
            password=user_data.password
        )
        
        return Token(**token_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при входе в систему"
        )


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_data: RefreshToken,
    db: AsyncSession = Depends(get_db)
):
    """
    Обновить access token используя refresh token
    
    - **refresh_token**: JWT refresh token
    
    Возвращает новый access token
    """
    try:
        # Обновляем access token
        token_data = await AuthService.refresh_access_token(
            db=db,
            refresh_token=refresh_data.refresh_token
        )
        
        return Token(**token_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при обновлении токена"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Получить информацию о текущем пользователе
    
    Требует авторизации
    """
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        is_activated=current_user.is_activated,
        created_at=current_user.created_at
    )


@router.post("/logout", response_model=MessageResponse)
async def logout_user(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Выход из системы
    
    Инвалидирует refresh token пользователя
    """
    try:
        await AuthService.logout_user(db=db, user_id=current_user.id)
        
        return MessageResponse(
            message="Выход выполнен успешно",
            success=True
        )
    except Exception as e:
        logger.error(f"Logout error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при выходе из системы"
        )
