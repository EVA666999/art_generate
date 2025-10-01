"""
Конфигурация для Mail service.
"""

import os
from dotenv import load_dotenv

# Загружаем .env файл из корня проекта
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
env_path = os.path.join(project_root, '.env')
# print(f"Looking for .env file at: {env_path}")  # Убрано для безопасности
load_dotenv(env_path)

# Email settings
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.mail.ru")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "True").lower() == "true"
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL")

# Проверяем обязательные переменные
if not EMAIL_HOST_USER:
    raise ValueError("EMAIL_HOST_USER not set in .env file")
if not EMAIL_HOST_PASSWORD:
    raise ValueError("EMAIL_HOST_PASSWORD not set in .env file")
if not DEFAULT_FROM_EMAIL:
    DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# Debug: print configuration (только в dev режиме)
if os.getenv("DEBUG_EMAIL", "false").lower() == "true":
    print(f"Email config loaded:")
    print(f"  EMAIL_HOST: {EMAIL_HOST}")
    print(f"  EMAIL_PORT: {EMAIL_PORT}")
    print(f"  EMAIL_USE_TLS: {EMAIL_USE_TLS}")
    print(f"  EMAIL_HOST_USER: {EMAIL_HOST_USER}")
    print(f"  EMAIL_HOST_PASSWORD: {'***' if EMAIL_HOST_PASSWORD else 'NOT SET'}")
    print(f"  DEFAULT_FROM_EMAIL: {DEFAULT_FROM_EMAIL}")

# Проверка уже выполнена выше