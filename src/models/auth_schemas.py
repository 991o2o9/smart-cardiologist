from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from datetime import datetime


class UserRegister(BaseModel):
    """Схема регистрации пользователя"""
    email: EmailStr = Field(..., description="Email пользователя")
    password: str = Field(..., min_length=8, description="Пароль (минимум 8 символов)")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "user@example.com",
                "password": "securepassword123"
            }
        }
    )


class UserLogin(BaseModel):
    """Схема входа пользователя"""
    email: EmailStr = Field(..., description="Email пользователя")
    password: str = Field(..., description="Пароль")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "user@example.com",
                "password": "securepassword123"
            }
        }
    )


class ActivationCode(BaseModel):
    """Схема активации аккаунта"""
    email: EmailStr = Field(..., description="Email пользователя")
    activation_code: str = Field(..., min_length=6, max_length=6, description="6-значный код активации")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "user@example.com",
                "activation_code": "123456"
            }
        }
    )


class ResendActivation(BaseModel):
    """Схема повторной отправки кода активации"""
    email: EmailStr = Field(..., description="Email пользователя")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "user@example.com"
            }
        }
    )


class Token(BaseModel):
    """Схема JWT токена"""
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Тип токена")
    expires_in: int = Field(..., description="Время жизни access token в минутах")
    refresh_expires_in: int = Field(..., description="Время жизни refresh token в днях")


class RefreshToken(BaseModel):
    """Схема для обновления токена"""
    refresh_token: str = Field(..., description="JWT refresh token")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }
    )


class TokenData(BaseModel):
    """Схема данных токена"""
    email: Optional[str] = None
    user_id: Optional[int] = None


class UserResponse(BaseModel):
    """Схема ответа с данными пользователя"""
    id: int = Field(..., description="ID пользователя")
    email: str = Field(..., description="Email пользователя")
    is_activated: bool = Field(..., description="Статус активации")
    created_at: datetime = Field(..., description="Дата создания")
    
    model_config = ConfigDict(from_attributes=True)


class MessageResponse(BaseModel):
    """Схема ответа с сообщением"""
    message: str = Field(..., description="Сообщение")
    success: bool = Field(..., description="Успешность операции")
