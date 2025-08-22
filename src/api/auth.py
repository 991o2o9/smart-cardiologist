from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from src.services.database import get_db
from src.services.auth_service import AuthService
from src.services.email_service import EmailService
from src.utils.auth_middleware import get_current_user
from src.models.auth_schemas import (
    UserRegister, UserLogin, ActivationCode, ResendActivation,
    Token, TokenRefreshResponse, RefreshToken, UserResponse, EmailStatusResponse, MessageResponse
)
from src.models.database import User
from pydantic import EmailStr
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Initialize services
email_service = EmailService()


@router.post("/register", response_model=MessageResponse)
async def register_user(
    user_data: UserRegister,
    db: AsyncSession = Depends(get_db)
):
    """
    Register new user
    
    - **email**: User email
    - **password**: Password (minimum 8 characters)
    """
    try:
        # Register user
        user = await AuthService.register_user(
            db=db,
            email=user_data.email,
            password=user_data.password
        )
        
        # Send activation email
        activation_sent = await email_service.send_activation_email(
            email=user.email,
            activation_code=user.activation_code
        )
        
        if not activation_sent:
            logger.warning(f"Failed to send activation email to {user.email}")
            # Can add retry logic or admin notification
        
        return MessageResponse(
            message="Registration successful! Check your email for activation code.",
            success=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error registering user"
        )


@router.post("/activate", response_model=MessageResponse)
async def activate_account(
    activation_data: ActivationCode,
    db: AsyncSession = Depends(get_db)
):
    """
    Activate account by code
    
    - **email**: User email
    - **activation_code**: 6-digit activation code
    """
    try:
        # Activate account
        success = await AuthService.activate_account(
            db=db,
            email=activation_data.email,
            activation_code=activation_data.activation_code
        )
        
        if success:
            # Send welcome email
            await email_service.send_welcome_email(activation_data.email)
            
            return MessageResponse(
                message="Account successfully activated! You can now log in to the system.",
                success=True
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Error activating account"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Activation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error activating account"
        )


@router.post("/resend-activation", response_model=MessageResponse)
async def resend_activation_code(
    resend_data: ResendActivation,
    db: AsyncSession = Depends(get_db)
):
    """
    Resend activation code
    
    - **email**: User email
    """
    try:
        # Generate new activation code
        new_code = await AuthService.resend_activation_code(
            db=db,
            email=resend_data.email
        )
        
        # Send new code
        email_sent = await email_service.send_activation_email(
            email=resend_data.email,
            activation_code=new_code
        )
        
        if email_sent:
            return MessageResponse(
                message="New activation code sent to your email.",
                success=True
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error sending email"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Resend activation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error sending activation code"
        )


@router.post("/login", response_model=Token)
async def login_user(
    user_data: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """
    Login to system
    
    - **email**: User email
    - **password**: Password
    
    Returns access token and refresh token
    """
    try:
        # Perform login
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
            detail="Error logging in to system"
        )


@router.post("/refresh", response_model=TokenRefreshResponse)
async def refresh_token(
    refresh_data: RefreshToken,
    db: AsyncSession = Depends(get_db)
):
    """
    Refresh access token using refresh token
    
    - **refresh_token**: JWT refresh token
    
    Returns new access token
    """
    try:
        # Refresh access token
        token_data = await AuthService.refresh_access_token(
            db=db,
            refresh_token=refresh_data.refresh_token
        )
        
        return TokenRefreshResponse(**token_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error refreshing token"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user information
    
    Requires authorization
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
    Logout from system
    
    Invalidates user's refresh token
    """
    try:
        await AuthService.logout_user(db=db, user_id=current_user.id)
        
        return MessageResponse(
            message="Logout successful",
            success=True
        )
    except Exception as e:
        logger.error(f"Logout error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error logging out from system"
        )


@router.get("/status", response_model=EmailStatusResponse)
async def check_email_status(
    email: EmailStr = Query(..., description="User email to check"),
    db: AsyncSession = Depends(get_db)
):
    """
    Check email activation status
    
    - **email**: User email to check (must be valid email format)
    
    Returns activation status and whether user exists
    """
    try:
        # Get user by email
        user = await AuthService.get_user_by_email(db=db, email=email)
        
        if user:
            return EmailStatusResponse(
                email=email,
                is_activated=user.is_activated,
                exists=True
            )
        else:
            return EmailStatusResponse(
                email=email,
                is_activated=False,
                exists=False
            )
            
    except Exception as e:
        logger.error(f"Email status check error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error checking email status"
        )
