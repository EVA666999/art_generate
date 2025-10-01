"""
Authentication dependencies.
"""

import jwt
import os
from datetime import datetime, timezone, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database.db_depends import get_db
from app.models.user import Users
from app.schemas.auth import TokenData

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Users:
    """Get current user by token."""
    import logging
    logger = logging.getLogger(__name__)
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            logger.warning("Email not found in token")
            raise credentials_exception
        token_data = TokenData(email=email)
        logger.debug(f"Token valid for user: {email}")
    except jwt.PyJWTError as e:
        logger.warning(f"Token decoding error: {e}")
        raise credentials_exception
    
    try:
        result = await db.execute(select(Users).filter(Users.email == token_data.email))
        user = result.scalar_one_or_none()
        if user is None:
            logger.warning(f"User not found: {email}")
            raise credentials_exception
        logger.debug(f"User found: {user.id}")
        return user
    except Exception as e:
        logger.error(f"Database error in get_current_user: {e}")
        raise credentials_exception


async def get_current_active_user(current_user: Users = Depends(get_current_user)) -> Users:
    """Get current active user."""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def create_jwt_token(data: dict, expires_delta: timedelta) -> str:
    """Создает JWT токен."""
    from datetime import datetime, timezone
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
