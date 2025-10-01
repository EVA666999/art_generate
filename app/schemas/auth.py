"""
Pydantic схемы для аутентификации.
"""

from datetime import datetime
import re
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator


class BaseSchema(BaseModel):
    """Базовая схема с настройками Pydantic."""
    
    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    """Схема для создания пользователя при регистрации"""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        """Валидация пароля"""
        if len(v) < 8:
            raise ValueError('Пароль должен содержать минимум 8 символов')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Пароль должен содержать хотя бы одну заглавную букву')
        if not re.search(r'[a-z]', v):
            raise ValueError('Пароль должен содержать хотя бы одну строчную букву')
        if not re.search(r'\d', v):
            raise ValueError('Пароль должен содержать хотя бы одну цифру')
        return v


class UserUpdate(BaseModel):
    """Схема для обновления пользователя"""
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None


class UserResponse(BaseModel):
    """Схема для ответа с пользователем"""
    id: int
    email: str
    is_active: bool
    is_admin: Optional[bool] = False  # Может быть None, по умолчанию False
    coins: int = 5
    created_at: Optional[datetime] = None
    subscription: Optional[dict] = None  # Информация о подписке

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    """Схема для входа пользователя"""
    email: EmailStr
    password: str
    verification_code: Optional[str] = None


class Token(BaseModel):
    """Схема для токена"""
    access_token: str
    token_type: str = "bearer"


class TokenResponse(BaseModel):
    """Схема для ответа с токенами"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    """Схема для обновления токена"""
    refresh_token: str


class TokenData(BaseModel):
    """Схема для данных токена"""
    email: Optional[str] = None


class Message(BaseModel):
    """Схема для сообщений"""
    message: str = Field(..., description="Сообщение")
