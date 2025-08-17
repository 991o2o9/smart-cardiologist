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

# Security scheme for JWT tokens
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Get current user by JWT token
    
    Args:
        credentials: JWT token from Authorization header
        db: Database session
        
    Returns:
        User: User object
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    try:
        # Verify token
        token_data = AuthService.verify_token(credentials.credentials)
        if token_data is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authorization token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Get user from database
        user = await db.execute(
            select(User).where(User.id == token_data.user_id)
        )
        user = user.scalar_one_or_none()
        
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Check if account is activated
        if not user.is_activated:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account not activated"
            )
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_current_user: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization error",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Get current active user
    
    Args:
        current_user: Current user
        
    Returns:
        User: Active user
    """
    # Additional checks can be added here
    # For example, account blocking check
    return current_user


def require_auth(func):
    """
    Decorator for routes requiring authorization
    
    Args:
        func: Route function
        
    Returns:
        Function with authorization dependency
    """
    # This decorator can be used for additional logic
    # In FastAPI, authorization is usually checked via Depends(get_current_user)
    return func
