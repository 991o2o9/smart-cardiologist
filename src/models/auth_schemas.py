from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime


class UserRegister(BaseModel):
    """User registration schema"""
    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., min_length=8, description="Password (minimum 8 characters)")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "user@example.com",
                "password": "securepassword123"
            }
        }
    )


class UserLogin(BaseModel):
    """User login schema"""
    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., description="Password")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "user@example.com",
                "password": "securepassword123"
            }
        }
    )


class ActivationCode(BaseModel):
    """Account activation schema"""
    email: EmailStr = Field(..., description="User email")
    activation_code: str = Field(..., min_length=6, max_length=6, description="6-digit activation code")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "user@example.com",
                "activation_code": "123456"
            }
        }
    )


class ResendActivation(BaseModel):
    """Resend activation code schema"""
    email: EmailStr = Field(..., description="User email")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "user@example.com"
            }
        }
    )


class Token(BaseModel):
    """JWT token schema"""
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Access token lifetime in minutes")
    refresh_expires_in: int = Field(..., description="Refresh token lifetime in days")


class TokenRefreshResponse(BaseModel):
    """JWT token refresh response schema"""
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Access token lifetime in minutes")
    refresh_expires_in: int = Field(..., description="Refresh token lifetime in days")


class RefreshToken(BaseModel):
    """Token refresh schema"""
    refresh_token: str = Field(..., description="JWT refresh token")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }
    )


class TokenData(BaseModel):
    """Token data schema"""
    email: Optional[str] = None
    user_id: Optional[int] = None


class UserResponse(BaseModel):
    """User data response schema"""
    id: int = Field(..., description="User ID")
    email: str = Field(..., description="User email")
    is_activated: bool = Field(..., description="Activation status")
    created_at: datetime = Field(..., description="Creation date")
    
    model_config = ConfigDict(from_attributes=True)


class EmailStatusResponse(BaseModel):
    """Email status response schema"""
    email: str = Field(..., description="User email")
    is_activated: bool = Field(..., description="Activation status")
    exists: bool = Field(..., description="Whether user exists")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "user@example.com",
                "is_activated": False,
                "exists": True
            }
        }
    )


class MessageResponse(BaseModel):
    """Message response schema"""
    message: str = Field(..., description="Message")
    success: bool = Field(..., description="Operation success")
