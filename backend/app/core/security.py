"""
Security module for authentication and authorization
Implements JWT token validation and user dependency injection
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from jose import jwt, JWTError
from typing import Optional, List

from app.db.database import get_db
from app.config import settings
from app.models.models import User, UserRole
from app.schema.auth_schema import TokenData

# HTTP Bearer token scheme
bearer_scheme = HTTPBearer(auto_error=True)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Dependency to get current authenticated user from JWT token
    
    Validates the access token and returns the corresponding user.
    Raises 401 if token is invalid or user not found.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode JWT token
        payload = jwt.decode(
            credentials.credentials, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        
        user_id: str = payload.get("sub")
        email: str = payload.get("email")
        
        if user_id is None:
            raise credentials_exception
        
        token_data = TokenData(user_id=int(user_id), email=email)
    except JWTError:
        raise credentials_exception
    
    # Get user from database
    result = await db.execute(
        select(User).where(User.id == token_data.user_id)
    )
    user = result.scalar_one_or_none()
    
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated"
        )
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Ensure current user is active
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user


def require_roles(allowed_roles: List[UserRole]):
    """
    Factory function to create role-based authorization dependency
    
    Usage:
        @router.get("/admin")
        async def admin_endpoint(user: User = Depends(require_roles([UserRole.SUPER_ADMIN]))):
            ...
    """
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{current_user.role.value}' not authorized for this endpoint"
            )
        return current_user
    
    return role_checker


# Pre-configured role dependencies
require_admin = require_roles([UserRole.SUPER_ADMIN, UserRole.SCHOOL_ADMIN])
require_teacher = require_roles([UserRole.TEACHER, UserRole.PRINCIPAL])
require_staff = require_roles([
    UserRole.TEACHER, UserRole.PRINCIPAL, UserRole.SCHOOL_ADMIN,
    UserRole.ACCOUNTANT, UserRole.LIBRARIAN, UserRole.TRANSPORT_MANAGER
])
require_parent = require_roles([UserRole.PARENT])


async def get_user_by_id(user_id: int, db: AsyncSession) -> Optional[User]:
    """Get user by ID"""
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


class RoleChecker:
    """
    Class-based role checker for more complex authorization scenarios
    """
    
    def __init__(self, allowed_roles: List[UserRole]):
        self.allowed_roles = allowed_roles
    
    async def __call__(self, current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {[r.value for r in self.allowed_roles]}"
            )
        return current_user
