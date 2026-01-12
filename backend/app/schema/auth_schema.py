"""
Pydantic schemas for User authentication and authorization
Following best practices for secure password handling and token generation
"""

from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional
from enum import Enum


class UserRoleEnum(str, Enum):
    SUPER_ADMIN = "super_admin"
    SCHOOL_ADMIN = "school_admin"
    PRINCIPAL = "principal"
    TEACHER = "teacher"
    ACCOUNTANT = "accountant"
    LIBRARIAN = "librarian"
    TRANSPORT_MANAGER = "transport_manager"
    PARENT = "parent"
    STUDENT = "student"
    SUPPORT = "support"


# ==================== Authentication Schemas ====================

class UserCreate(BaseModel):
    """Schema for creating a new user account"""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, max_length=128, description="Secure password")
    role: UserRoleEnum = Field(..., description="User role")
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    gender: Optional[str] = None


class UserLogin(BaseModel):
    """Schema for user login request"""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")


class UserResponse(BaseModel):
    """Schema for user response (excluding sensitive data)"""
    id: int
    email: str
    role: UserRoleEnum
    is_active: bool
    is_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserProfileResponse(BaseModel):
    """Schema for user profile response"""
    id: int
    user_id: int
    first_name: str
    last_name: str
    phone: Optional[str]
    address: Optional[str]
    photo_url: Optional[str]
    date_of_birth: Optional[datetime]
    gender: Optional[str]
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    """Schema for JWT token response"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int = Field(..., description="Token expiration time in seconds")
    user: UserResponse


class TokenData(BaseModel):
    """Schema for token payload data"""
    user_id: Optional[int] = None
    email: Optional[str] = None
    role: Optional[str] = None
    exp: Optional[datetime] = None


class PasswordResetRequest(BaseModel):
    """Schema for password reset request"""
    email: EmailStr = Field(..., description="Email address to send reset link")


class PasswordResetConfirm(BaseModel):
    """Schema for password reset confirmation"""
    token: str = Field(..., description="Reset token from email")
    new_password: str = Field(..., min_length=8, max_length=128)


class ChangePassword(BaseModel):
    """Schema for changing password (authenticated)"""
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, max_length=128, description="New password")


class RefreshTokenRequest(BaseModel):
    """Schema for refreshing access token"""
    refresh_token: str = Field(..., description="Valid refresh token")


# ==================== API Response Schemas ====================

class ApiResponse(BaseModel):
    """Generic API response wrapper"""
    success: bool
    message: str
    data: Optional[dict] = None


class PaginatedResponse(BaseModel):
    """Paginated response wrapper"""
    success: bool
    message: str
    data: list
    total: int
    page: int
    per_page: int
    total_pages: int


class ErrorResponse(BaseModel):
    """Error response schema"""
    success: bool = False
    message: str
    detail: Optional[str] = None
    errors: Optional[dict] = None
