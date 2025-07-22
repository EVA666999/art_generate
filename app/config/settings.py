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
    
    # Text Generation WebUI настройки
    text_generation_webui_path: str = str(BASE_DIR / "text-generation-webui")
    text_generation_webui_host: str = "127.0.0.1"
    text_generation_webui_port: int = 7861
    text_generation_webui_model: str = "Llama-3.1-128k-Dark-Planet-Uncensored-8B-Q4_k_s.gguf"
    text_generation_webui_loader: str = "llama.cpp"
    text_generation_webui_model_dir: str = str(BASE_DIR / "text-generation-webui" / "models" / "main_model")
    
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

def generate_bat():
    """Генерирует start_webui_with_api.bat с актуальным именем модели из настроек."""
    with open("start_webui_with_api.bat", "w", encoding="utf-8") as f:
        f.write(f"""@echo off
cd /D "%~dp0"
cd text-generation-webui
python server.py --api --api-port 5000 --listen --listen-port 7861 --model {settings.text_generation_webui_model} --loader llama.cpp --model-dir models/main_model
pause
""") 