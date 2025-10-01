"""
Роутеры для аутентификации.
"""

from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, HTTPException, Request, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.auth import (
    UserCreate, UserLogin, UserResponse, 
    TokenResponse, RefreshTokenRequest, Message
)
from app.database.db_depends import get_db
from app.models.user import Users, RefreshToken, EmailVerificationCode
from app.auth.utils import (
    hash_password, verify_password, hash_token, 
    create_refresh_token, get_token_expiry, generate_verification_code, send_verification_email
)
from app.auth.rate_limiter import get_rate_limiter, RateLimiter
from app.auth.dependencies import get_current_user
from app.services.subscription_service import SubscriptionService
import jwt
import os
import time

auth_router = APIRouter()

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7


def create_jwt_token(data: dict, expires_delta: timedelta) -> str:
    """Creates JWT token with specified expiration time."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def activate_base_subscription(user_id: int, db: AsyncSession) -> None:
    """Активирует подписку Base для нового пользователя."""
    try:
        print(f"[DEBUG] Активация подписки Base для пользователя {user_id}")
        subscription_service = SubscriptionService(db)
        await subscription_service.create_subscription(user_id, "base")
        print(f"[OK] Подписка Base успешно активирована для пользователя {user_id}")
    except Exception as e:
        print(f"[ERROR] Ошибка активации подписки Base для пользователя {user_id}: {e}")
        # Не прерываем регистрацию из-за ошибки подписки


@auth_router.post("/auth/register/", response_model=UserResponse)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Registers a new user.

    Parameters:
    - user: Data for registering a new user.

    Returns:
    - UserResponse: Registered user.
    """
    # Log registration start
    print(f"Starting registration for email: {user.email}")
    
    # Check if user already exists
    result = await db.execute(select(Users).filter(Users.email == user.email))
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    # Hash password
    hashed_password = hash_password(user.password)
    
    # Create new user
    db_user = Users(
        email=user.email,
        password_hash=hashed_password,
        is_active=True,
        is_verified=False
    )
    
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    
    # Активируем подписку Base для нового пользователя
    await activate_base_subscription(db_user.id, db)
    
    # Generate verification code
    verification_code = generate_verification_code()
    expires_at = get_token_expiry(days=1)  # Code expires in 1 day
    
    # Save verification code
    verification = EmailVerificationCode(
        user_id=db_user.id,
        code=verification_code,
        expires_at=expires_at
    )
    db.add(verification)
    await db.commit()
    
    # Send verification email
    await send_verification_email(user.email, verification_code)
    
    print(f"User {user.email} registered successfully")
    
    return UserResponse(
        id=db_user.id,
        email=db_user.email,
        is_active=db_user.is_active,
        created_at=db_user.created_at
    )


@auth_router.post("/auth/login/", response_model=TokenResponse)
async def login_user(
    user_credentials: UserLogin, 
    db: AsyncSession = Depends(get_db),
    rate_limiter: RateLimiter = Depends(get_rate_limiter)
):
    """
    Authenticates user and returns tokens.

    Parameters:
    - user_credentials: User login credentials.
    - db: Database session.
    - rate_limiter: Rate limiter instance.

    Returns:
    - TokenResponse: Access and refresh tokens.
    """
    # Rate limiting
    if not rate_limiter.is_allowed(user_credentials.email):
        raise HTTPException(
            status_code=429,
            detail="Too many requests. Please try again later."
        )
    
    # Find user
    result = await db.execute(select(Users).filter(Users.email == user_credentials.email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(user_credentials.password, user.password_hash):
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=400,
            detail="Inactive user"
        )
    
    # Check verification code if provided
    if user_credentials.verification_code:
        result = await db.execute(select(EmailVerificationCode).filter(
            EmailVerificationCode.user_id == user.id,
            EmailVerificationCode.code == user_credentials.verification_code,
            EmailVerificationCode.is_used == False,
            EmailVerificationCode.expires_at > datetime.now(timezone.utc).replace(tzinfo=None)
        ))
        verification = result.scalar_one_or_none()
        
        if not verification:
            raise HTTPException(
                status_code=400,
                detail="Invalid or expired verification code"
            )
        
        # Mark verification code as used
        verification.is_used = True
        user.is_verified = True
        await db.commit()
    
    # Create tokens
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_jwt_token(
        data={"sub": user.email}, 
        expires_delta=access_token_expires
    )
    
    refresh_token = create_refresh_token()
    refresh_token_hash = hash_token(refresh_token)
    refresh_expires = get_token_expiry(REFRESH_TOKEN_EXPIRE_DAYS)
    
    # Save refresh token
    db_refresh_token = RefreshToken(
        user_id=user.id,
        token_hash=refresh_token_hash,
        expires_at=refresh_expires
    )
    db.add(db_refresh_token)
    await db.commit()
    
    # Проверяем и активируем подписку Base, если её нет
    try:
        subscription_service = SubscriptionService(db)
        existing_subscription = await subscription_service.get_user_subscription(user.id)
        if not existing_subscription:
            print(f"[DEBUG] У пользователя {user.email} нет подписки, активируем Base")
            await subscription_service.create_subscription(user.id, "base")
            print(f"[OK] Подписка Base активирована для пользователя {user.email}")
    except Exception as e:
        print(f"[ERROR] Ошибка проверки/активации подписки для пользователя {user.email}: {e}")
    
    print(f"User {user.email} logged in successfully")
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )


@auth_router.post("/auth/refresh/", response_model=TokenResponse)
async def refresh_token(
    refresh_request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Refreshes access token using refresh token.

    Parameters:
    - refresh_request: Refresh token request.
    - db: Database session.

    Returns:
    - TokenResponse: New access and refresh tokens.
    """
    refresh_token_hash = hash_token(refresh_request.refresh_token)
    
    # Find refresh token
    result = await db.execute(select(RefreshToken).filter(
        RefreshToken.token_hash == refresh_token_hash,
        RefreshToken.is_active == True,
        RefreshToken.expires_at > datetime.now(timezone.utc).replace(tzinfo=None)
    ))
    db_refresh_token = result.scalar_one_or_none()
    
    if not db_refresh_token:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired refresh token"
        )
    
    # Get user
    result = await db.execute(select(Users).filter(Users.id == db_refresh_token.user_id))
    user = result.scalar_one_or_none()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=401,
            detail="User not found or inactive"
        )
    
    # Deactivate old refresh token
    db_refresh_token.is_active = False
    
    # Create new tokens
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_jwt_token(
        data={"sub": user.email}, 
        expires_delta=access_token_expires
    )
    
    new_refresh_token = create_refresh_token()
    new_refresh_token_hash = hash_token(new_refresh_token)
    refresh_expires = get_token_expiry(REFRESH_TOKEN_EXPIRE_DAYS)
    
    # Save new refresh token
    new_db_refresh_token = RefreshToken(
        user_id=user.id,
        token_hash=new_refresh_token_hash,
        expires_at=refresh_expires
    )
    db.add(new_db_refresh_token)
    await db.commit()
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        token_type="bearer"
    )


@auth_router.post("/auth/logout/", response_model=Message)
async def logout_user(
    refresh_request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Logs out user by deactivating refresh token.

    Parameters:
    - refresh_request: Refresh token request.
    - db: Database session.

    Returns:
    - Message: Logout confirmation.
    """
    refresh_token_hash = hash_token(refresh_request.refresh_token)
    
    # Find and deactivate refresh token
    result = await db.execute(select(RefreshToken).filter(
        RefreshToken.token_hash == refresh_token_hash,
        RefreshToken.is_active == True
    ))
    db_refresh_token = result.scalar_one_or_none()
    
    if db_refresh_token:
        db_refresh_token.is_active = False
        await db.commit()
    
    return Message(message="Successfully logged out")


@auth_router.get("/auth/me/", response_model=UserResponse)
async def get_current_user_info(
    current_user: Users = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get current user information.

    Parameters:
    - current_user: Current authenticated user.
    - db: Database session.

    Returns:
    - UserResponse: Current user information.
    """
    try:
        # Загружаем пользователя с подпиской явно
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload
        
        stmt = select(Users).options(selectinload(Users.subscription)).filter(Users.id == current_user.id)
        result = await db.execute(stmt)
        user_with_subscription = result.scalar_one_or_none()
        
        # Получаем информацию о подписке
        subscription_info = None
        if user_with_subscription and user_with_subscription.subscription:
            subscription_info = {
                "subscription_type": user_with_subscription.subscription.subscription_type.value,
                "status": user_with_subscription.subscription.status.value,
                "monthly_credits": user_with_subscription.subscription.monthly_credits,
                "monthly_photos": user_with_subscription.subscription.monthly_photos,
                "max_message_length": user_with_subscription.subscription.max_message_length,
                "used_credits": user_with_subscription.subscription.used_credits,
                "used_photos": user_with_subscription.subscription.used_photos,
                "activated_at": user_with_subscription.subscription.activated_at,
                "expires_at": user_with_subscription.subscription.expires_at
            }
        
        return UserResponse(
            id=current_user.id,
            email=current_user.email,
            is_active=current_user.is_active,
            is_admin=current_user.is_admin if current_user.is_admin is not None else False,
            coins=current_user.coins,
            created_at=current_user.created_at,
            subscription=subscription_info
        )
    except Exception as e:
        # Если есть ошибка с подпиской, возвращаем пользователя без подписки
        return UserResponse(
            id=current_user.id,
            email=current_user.email,
            is_active=current_user.is_active,
            is_admin=current_user.is_admin if current_user.is_admin is not None else False,
            coins=current_user.coins,
            created_at=current_user.created_at,
            subscription=None
        )


@auth_router.get("/auth/coins/")
async def get_user_coins(current_user: Users = Depends(get_current_user)):
    """Получить количество монет пользователя."""
    return {"coins": current_user.coins}


@auth_router.post("/auth/coins/add/")
async def add_coins(
    amount: int,
    current_user: Users = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Добавить монеты пользователю (для админов или тестирования)."""
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")
    
    current_user.coins += amount
    await db.commit()
    await db.refresh(current_user)
    
    return {"coins": current_user.coins, "added": amount}


@auth_router.post("/auth/coins/spend/")
async def spend_coins(
    amount: int,
    current_user: Users = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Потратить монеты пользователя."""
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")
    
    if current_user.coins < amount:
        raise HTTPException(status_code=400, detail="Insufficient coins")
    
    current_user.coins -= amount
    await db.commit()
    await db.refresh(current_user)
    
    return {"coins": current_user.coins, "spent": amount}
