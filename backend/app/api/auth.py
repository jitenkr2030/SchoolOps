"""
Authentication API endpoints
Implements secure JWT-based authentication with bcrypt password hashing
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
from typing import Optional

from app.db.database import get_db
from app.schema.auth_schema import (
    UserCreate, UserLogin, UserResponse, Token, 
    PasswordResetRequest, PasswordResetConfirm, ChangePassword,
    ApiResponse, ErrorResponse
)
from app.config import settings
from app.models.models import User, UserProfile, UserRole

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Authentication router
router = APIRouter(prefix="/auth", tags=["Authentication"])


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate password hash"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(user_id: int) -> str:
    """Create JWT refresh token"""
    expire = datetime.utcnow() + timedelta(days=7)
    data = {"sub": str(user_id), "type": "refresh", "exp": expire}
    return jwt.encode(data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """Get user by email address"""
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def create_user_profile(db: AsyncSession, user: User, first_name: str, 
                               last_name: str, phone: Optional[str] = None,
                               address: Optional[str] = None,
                               date_of_birth: Optional[datetime] = None,
                               gender: Optional[str] = None) -> UserProfile:
    """Create user profile"""
    profile = UserProfile(
        user_id=user.id,
        first_name=first_name,
        last_name=last_name,
        phone=phone,
        address=address,
        date_of_birth=date_of_birth,
        gender=gender
    )
    db.add(profile)
    await db.flush()
    return profile


@router.post("/register", response_model=ApiResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Register a new user account
    
    Creates both User and UserProfile records with hashed password.
    Role determines system permissions.
    """
    # Check if user already exists
    existing_user = await get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        email=user_data.email,
        password_hash=hashed_password,
        role=user_data.role,
        is_active=True,
        is_verified=False
    )
    db.add(db_user)
    await db.flush()  # Get the user ID
    
    # Create user profile
    await create_user_profile(
        db, db_user,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        phone=user_data.phone,
        address=user_data.address,
        date_of_birth=user_data.date_of_birth,
        gender=user_data.gender
    )
    
    await db.commit()
    
    return ApiResponse(
        success=True,
        message="User registered successfully",
        data={"user_id": db_user.id, "email": db_user.email}
    )


@router.post("/login", response_model=Token)
async def login(credentials: UserLogin, db: AsyncSession = Depends(get_db)):
    """
    Authenticate user and return JWT tokens
    
    Returns access token (short-lived) and refresh token (long-lived).
    """
    # Find user
    user = await get_user_by_email(db, credentials.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify password
    if not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is deactivated. Please contact administrator."
        )
    
    # Generate tokens
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email, "role": user.role.value},
        expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(user.id)
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse(
            id=user.id,
            email=user.email,
            role=user.role,
            is_active=user.is_active,
            is_verified=user.is_verified,
            created_at=user.created_at
        )
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(refresh_token: str, db: AsyncSession = Depends(get_db)):
    """
    Refresh access token using valid refresh token
    """
    try:
        payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")
        
        if token_type != "refresh" or not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Get user
        result = await db.execute(select(User).where(User.id == int(user_id)))
        user = result.scalar_one_or_none()
        
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        # Generate new access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email, "role": user.role.value},
            expires_delta=access_token_expires
        )
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=UserResponse(
                id=user.id,
                email=user.email,
                role=user.role,
                is_active=user.is_active,
                is_verified=user.is_verified,
                created_at=user.created_at
            )
        )
        
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )


@router.post("/change-password", response_model=ApiResponse)
async def change_password(
    password_data: ChangePassword,
    current_user: User = Depends(lambda: None),  # Will be replaced with actual dependency
    db: AsyncSession = Depends(get_db)
):
    """
    Change password for authenticated user
    """
    # Note: This will be implemented with proper authentication dependency
    # For now, it's a placeholder showing the expected flow
    
    # Get user from token (actual implementation in security.py)
    # user = await get_current_user(...)
    
    # Verify current password
    # if not verify_password(password_data.current_password, user.password_hash):
    #     raise HTTPException(status_code=400, detail="Current password is incorrect")
    
    # Update password
    # hashed_password = get_password_hash(password_data.new_password)
    # await db.execute(update(User).where(User.id == user.id).values(password_hash=hashed_password))
    # await db.commit()
    
    return ApiResponse(
        success=True,
        message="Password changed successfully"
    )


@router.post("/logout", response_model=ApiResponse)
async def logout():
    """
    Logout user (client-side token removal)
    
    Note: For stateless JWT, logout is handled client-side by removing the token.
    For stateful logout, implement a token blacklist in Redis.
    """
    return ApiResponse(
        success=True,
        message="Logged out successfully"
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(lambda: None)  # Will be replaced with actual dependency
):
    """
    Get current authenticated user's information
    """
    # Note: Will be implemented with proper authentication dependency
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        role=current_user.role,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
        created_at=current_user.created_at
    )
