"""
Настройки приложения
"""
import os
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings
from functools import lru_cache
from pathlib import Path
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

class Settings(BaseSettings):
    """Настройки приложения"""
    # API настройки
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    
    # Пути к файлам
    BASE_DIR: Path = Path(__file__).parent.parent.parent
    OUTPUT_DIR: Path = BASE_DIR / "outputs"
    LORA_DIR: Path = BASE_DIR / "loras"
    
    # Настройки Stable Diffusion
    MODEL_NAME: str = "dreamshaper_8.safetensors"
    VAE_NAME: Optional[str] = None
    LORA_NAME: Optional[str] = None
    
    # Параметры генерации по умолчанию
    DEFAULT_STEPS: int = 20
    DEFAULT_CFG_SCALE: float = 7.0
    DEFAULT_WIDTH: int = 512
    DEFAULT_HEIGHT: int = 512
    DEFAULT_SAMPLER: str = "DPM++ 2M Karras"
    
    # API URLs
    SD_API_URL: str = "http://127.0.0.1:7860"  # URL для Stable Diffusion WebUI API
    WEBUI_URL: str = "http://127.0.0.1:7860"  # URL для Stable Diffusion WebUI
    SD_API_TIMEOUT: float = 600.0  # Таймаут для API запросов в секундах
    
    # Default Prompts
    USE_DEFAULT_PROMPTS: bool = True  # Использовать дефолтные промпты
    DEFAULT_PROMPTS_WEIGHT: float = 1.0  # Вес дефолтных промптов
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./sql_app.db"
    POSTGRES_DB: str = "art_generate_db"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "Kohkau11999"
    DB_HOST: str = "localhost"
    DB_PORT: str = "5432"
    
    # Security
    SECRET_KEY: str = "your-super-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # Hugging Face
    HUGGINGFACE_TOKEN: str = "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"
    
    # Performance
    MAX_WORKERS: int = 4
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "env_prefix": "",
        "extra": "ignore",
        "protected_namespaces": ()
    }

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings() 