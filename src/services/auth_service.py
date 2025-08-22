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
from models.database import User
from models.auth_schemas import TokenData
import logging

logger = logging.getLogger(__name__)

# Контекст для хэширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """Service for authentication operations"""
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify password"""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """Get password hash"""
        return pwd_context.hash(password)
    
    @staticmethod
    def generate_activation_code() -> str:
        """Generate 6-digit activation code"""
        return ''.join(secrets.choice(string.digits) for _ in range(6))
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
        """Create JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None):
        """Create JWT refresh token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str, token_type: str = "access") -> Optional[TokenData]:
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            email: str = payload.get("sub")
            user_id: int = payload.get("user_id")
            token_type_payload: str = payload.get("type")
            
            if email is None or token_type_payload != token_type:
                return None
                
            return TokenData(email=email, user_id=user_id)
        except JWTError:
            return None
    
    @classmethod
    async def register_user(cls, db: AsyncSession, email: str, password: str) -> User:
        """Register new user"""
        # Check if user exists
        existing_user = await db.execute(
            select(User).where(User.email == email)
        )
        if existing_user.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        
        # Create user
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
        """Activate user account"""
        user = await db.execute(
            select(User).where(User.email == email)
        )
        user = user.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        if user.is_activated:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Account is already activated"
            )
        
        # Check attempt count
        if user.activation_attempts >= settings.MAX_ACTIVATION_ATTEMPTS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum activation attempts exceeded. Request a new code."
            )
        
        # Check code and expiration
        if (user.activation_code != activation_code or 
            user.activation_code_expires < datetime.utcnow()):
            
            # Increment attempt counter
            await db.execute(
                update(User)
                .where(User.id == user.id)
                .values(activation_attempts=User.activation_attempts + 1)
            )
            await db.commit()
            
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid activation code or code expired"
            )
        
        # Activate account
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
        """Send new activation code"""
        user = await db.execute(
            select(User).where(User.email == email)
        )
        user = user.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        if user.is_activated:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Account is already activated"
            )
        
        # Generate new code
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
        """Authenticate user"""
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
        """Get current user by token"""
        token_data = cls.verify_token(token, "access")
        if token_data is None:
            return None
        
        user = await db.execute(
            select(User).where(User.id == token_data.user_id)
        )
        return user.scalar_one_or_none()
    
    @classmethod
    async def login_user(cls, db: AsyncSession, email: str, password: str) -> dict:
        """Login to system"""
        user = await cls.authenticate_user(db, email, password)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        if not user.is_activated:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Account not activated. Check your email for activation code."
            )
        
        # Create tokens
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        
        access_token = cls.create_access_token(
            data={"sub": user.email, "user_id": user.id},
            expires_delta=access_token_expires
        )
        
        refresh_token = cls.create_refresh_token(
            data={"sub": user.email, "user_id": user.id},
            expires_delta=refresh_token_expires
        )
        
        # Save refresh token in database
        await db.execute(
            update(User)
            .where(User.id == user.id)
            .values(
                refresh_token=refresh_token,
                refresh_token_expires=datetime.utcnow() + refresh_token_expires
            )
        )
        await db.commit()
        
        logger.info(f"User logged in: {email}")
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES,
            "refresh_expires_in": settings.REFRESH_TOKEN_EXPIRE_DAYS
        }
    
    @classmethod
    async def refresh_access_token(cls, db: AsyncSession, refresh_token: str) -> dict:
        """Refresh access token using refresh token"""
        # Verify refresh token
        token_data = cls.verify_token(refresh_token, "refresh")
        if token_data is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Get user
        user = await db.execute(
            select(User).where(User.id == token_data.user_id)
        )
        user = user.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        # Check if refresh token in database matches
        if user.refresh_token != refresh_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Check refresh token expiration
        if user.refresh_token_expires < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token expired"
            )
        
        # Create new access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        new_access_token = cls.create_access_token(
            data={"sub": user.email, "user_id": user.id},
            expires_delta=access_token_expires
        )
        
        logger.info(f"Access token refreshed for user: {user.email}")
        return {
            "access_token": new_access_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES
        }
    
    @classmethod
    async def logout_user(cls, db: AsyncSession, user_id: int) -> bool:
        """Logout from system (invalidate refresh token)"""
        await db.execute(
            update(User)
            .where(User.id == user_id)
            .values(
                refresh_token=None,
                refresh_token_expires=None
            )
        )
        await db.commit()
        
        logger.info(f"User logged out: {user_id}")
        return True

    @classmethod
    async def get_user_by_email(cls, db: AsyncSession, email: str) -> Optional[User]:
        """Get user by email"""
        result = await db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
