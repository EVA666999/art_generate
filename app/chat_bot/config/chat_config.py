"""
Конфигурация для чат-бота с настраиваемым характером.
"""
import os
from typing import Optional, Dict, Any
from pydantic_settings import BaseSettings
from pydantic import Field


class ChatConfig(BaseSettings):
    """Конфигурация чат-бота."""
    
    # Путь к модели
    MODEL_PATH: str = Field(
        default="D:/lm_models/DavidAU/Llama-3.2-8X3B-MOE-Dark-Champion-Instruct-uncensored-abliterated-18.4B-GGUF/L3.2-8X3B-MOE-Dark-Champion-Inst-18.4B-uncen-ablit_D_AU-Q4_k_s.gguf",
        description="Путь к GGUF модели"
    )
    
    # Параметры модели
    N_CTX: int = Field(default=4096, description="Размер контекста (увеличен для GPU)")
    N_GPU_LAYERS: int = Field(default=35, description="Количество слоев на GPU (35 для RTX 3060)")
    N_THREADS: int = Field(default=8, description="Количество потоков CPU")
    N_BATCH: int = Field(default=512, description="Размер батча (увеличен для GPU)")
    
    # Параметры генерации по умолчанию
    DEFAULT_MAX_TOKENS: int = Field(default=512, description="Максимальное количество токенов по умолчанию")
    DEFAULT_TEMPERATURE: float = Field(default=0.8, description="Температура по умолчанию")
    DEFAULT_TOP_P: float = Field(default=0.9, description="Top-p по умолчанию")
    DEFAULT_TOP_K: int = Field(default=40, description="Top-k по умолчанию")
    DEFAULT_REPEAT_PENALTY: float = Field(default=1.1, description="Штраф за повторения по умолчанию")
    
    # Лимиты
    MAX_HISTORY_LENGTH: int = Field(default=20, description="Максимальная длина истории диалога")
    MAX_MESSAGE_LENGTH: int = Field(default=2000, description="Максимальная длина сообщения")
    MAX_CHARACTER_NAME_LENGTH: int = Field(default=50, description="Максимальная длина имени персонажа")
    
    # Настройки безопасности
    ENABLE_CONTENT_FILTER: bool = Field(default=False, description="Включить фильтрацию контента")
    FORBIDDEN_WORDS: list = Field(default=[], description="Запрещенные слова")
    
    # Настройки логирования
    LOG_CHAT_REQUESTS: bool = Field(default=True, description="Логировать запросы чата")
    LOG_CHAT_RESPONSES: bool = Field(default=False, description="Логировать ответы чата")
    
    # Настройки производительности
    ENABLE_CACHE: bool = Field(default=True, description="Включить кэширование")
    CACHE_TTL: int = Field(default=3600, description="Время жизни кэша в секундах")
    MAX_CACHE_SIZE: int = Field(default=1000, description="Максимальный размер кэша")
    
    class Config:
        env_prefix = "CHAT_"
        case_sensitive = False


# Создаем экземпляр конфигурации
chat_config = ChatConfig() 