import secrets
import string
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import HTTPException, status
from config.settings import settings
from src.models.database import User
from src.models.auth_schemas import TokenData
import logging

logger = logging.getLogger(__name__)

# Контекст для хэширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """Сервис для работы с авторизацией"""
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Проверить пароль"""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """Получить хэш пароля"""
        return pwd_context.hash(password)
    
    @staticmethod
    def generate_activation_code() -> str:
        """Сгенерировать 6-значный код активации"""
        return ''.join(secrets.choice(string.digits) for _ in range(6))
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
        """Создать JWT токен"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> Optional[TokenData]:
        """Проверить JWT токен"""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            email: str = payload.get("sub")
            user_id: int = payload.get("user_id")
            
            if email is None:
                return None
                
            return TokenData(email=email, user_id=user_id)
        except JWTError:
            return None
    
    @classmethod
    async def register_user(cls, db: AsyncSession, email: str, password: str) -> User:
        """Зарегистрировать нового пользователя"""
        # Проверяем, существует ли пользователь
        existing_user = await db.execute(
            select(User).where(User.email == email)
        )
        if existing_user.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пользователь с таким email уже существует"
            )
        
        # Создаем пользователя
        activation_code = cls.generate_activation_code()
        activation_expires = datetime.utcnow() + timedelta(minutes=settings.ACTIVATION_CODE_EXPIRE_MINUTES)
        
        user = User(
            email=email,
            password_hash=cls.get_password_hash(password),
            activation_code=activation_code,
            activation_code_expires=activation_expires,
            is_activated=False
        )
        
        db.add(user)
        await db.commit()
        await db.refresh(user)
        
        logger.info(f"User registered: {email}")
        return user
    
    @classmethod
    async def activate_account(cls, db: AsyncSession, email: str, activation_code: str) -> bool:
        """Активировать аккаунт пользователя"""
        user = await db.execute(
            select(User).where(User.email == email)
        )
        user = user.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден"
            )
        
        if user.is_activated:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Аккаунт уже активирован"
            )
        
        # Проверяем количество попыток
        if user.activation_attempts >= settings.MAX_ACTIVATION_ATTEMPTS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Превышено количество попыток активации. Запросите новый код."
            )
        
        # Проверяем код и срок действия
        if (user.activation_code != activation_code or 
            user.activation_code_expires < datetime.utcnow()):
            
            # Увеличиваем счетчик попыток
            await db.execute(
                update(User)
                .where(User.id == user.id)
                .values(activation_attempts=User.activation_attempts + 1)
            )
            await db.commit()
            
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Неверный код активации или код истек"
            )
        
        # Активируем аккаунт
        await db.execute(
            update(User)
            .where(User.id == user.id)
            .values(
                is_activated=True,
                activation_code=None,
                activation_code_expires=None,
                activation_attempts=0
            )
        )
        await db.commit()
        
        logger.info(f"Account activated: {email}")
        return True
    
    @classmethod
    async def resend_activation_code(cls, db: AsyncSession, email: str) -> str:
        """Отправить новый код активации"""
        user = await db.execute(
            select(User).where(User.email == email)
        )
        user = user.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден"
            )
        
        if user.is_activated:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Аккаунт уже активирован"
            )
        
        # Генерируем новый код
        new_activation_code = cls.generate_activation_code()
        new_expires = datetime.utcnow() + timedelta(minutes=settings.ACTIVATION_CODE_EXPIRE_MINUTES)
        
        await db.execute(
            update(User)
            .where(User.id == user.id)
            .values(
                activation_code=new_activation_code,
                activation_code_expires=new_expires,
                activation_attempts=0
            )
        )
        await db.commit()
        
        logger.info(f"New activation code sent: {email}")
        return new_activation_code
    
    @classmethod
    async def authenticate_user(cls, db: AsyncSession, email: str, password: str) -> Optional[User]:
        """Аутентифицировать пользователя"""
        user = await db.execute(
            select(User).where(User.email == email)
        )
        user = user.scalar_one_or_none()
        
        if not user:
            return None
        
        if not cls.verify_password(password, user.password_hash):
            return None
        
        return user
    
    @classmethod
    async def get_current_user(cls, db: AsyncSession, token: str) -> Optional[User]:
        """Получить текущего пользователя по токену"""
        token_data = cls.verify_token(token)
        if token_data is None:
            return None
        
        user = await db.execute(
            select(User).where(User.id == token_data.user_id)
        )
        return user.scalar_one_or_none()
    
    @classmethod
    async def login_user(cls, db: AsyncSession, email: str, password: str) -> dict:
        """Войти в систему"""
        user = await cls.authenticate_user(db, email, password)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный email или пароль"
            )
        
        if not user.is_activated:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Аккаунт не активирован. Проверьте email для получения кода активации."
            )
        
        # Создаем токен
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = cls.create_access_token(
            data={"sub": user.email, "user_id": user.id},
            expires_delta=access_token_expires
        )
        
        logger.info(f"User logged in: {email}")
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES
        }
