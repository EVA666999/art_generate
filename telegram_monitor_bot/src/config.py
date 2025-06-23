"""
Конфигурация бота
"""
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

class Settings(BaseSettings):
    """Настройки бота"""
    BOT_TOKEN: str
    USER_ID: int
    API_ID: int
    API_HASH: str
    
    # Путь к основному проекту (обязательный параметр)
    MAIN_PROJECT_PATH: Path
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "env_prefix": "",
        "extra": "allow",
        "protected_namespaces": ()
    }

    def get_log_path(self) -> Path:
        """
        Получение пути к файлу логов
        
        Returns:
            Path: Путь к файлу логов
        """
        # Путь к файлу логов в основном проекте
        return self.MAIN_PROJECT_PATH / "app" / "data" / "generation_stats.json"

# Создаем экземпляр настроек
settings = Settings()

# Путь к файлу с логами
LOG_FILE = settings.get_log_path()