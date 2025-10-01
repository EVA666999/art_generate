"""
Утилиты для аутентификации.
"""

import hashlib
import secrets
import random
import string
from datetime import datetime, timezone, timedelta


def hash_password(password: str) -> str:
    """Хеширует пароль используя SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, hashed: str) -> bool:
    """Проверяет пароль против хеша."""
    return hash_password(password) == hashed


def hash_token(token: str) -> str:
    """Хеширует токен используя SHA-256."""
    return hashlib.sha256(token.encode()).hexdigest()


def create_refresh_token() -> str:
    """Создает случайный refresh токен."""
    return secrets.token_urlsafe(32)


def get_token_expiry(days: int = 7) -> datetime:
    """Возвращает время истечения токена (timezone-naive)."""
    return datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(days=days)


def generate_verification_code() -> str:
    """Генерирует 6-значный код верификации."""
    return ''.join(random.choices(string.digits, k=6))


async def send_verification_email(email: str, code: str) -> None:
    """
    Отправляет код верификации на email.
    """
    try:
        from app.mail_service.sender import EmailSender
        email_sender = EmailSender()
        success = email_sender.send_verification_email(email, code)
        
        if not success:
            print(f"Verification code {code} for {email} (real sending disabled)")
            
    except Exception as e:
        print(f"Error sending email: {e}")
        print(f"Verification code {code} for {email} (email sending disabled)")