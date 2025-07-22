"""
Конфигурация для чат-бота с настраиваемым характером.
Оптимизирована для модели DavidAU.L3.1-Dark-Reasoning-
LewdPlay-evo-Hermes-R1-Uncensored-8B
"""
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field
from app.utils.cpu_utils import get_cpu_info, get_optimal_batch_size
import os


class ChatConfig(BaseSettings):
    """Конфигурация чат-бота."""

    # Параметры модели (АВТОМАТИЧЕСКИ ОПТИМИЗИРОВАНЫ для вашего CPU/GPU)
    N_CTX: int = Field(
        default=1024,  # Уменьшено для максимальной скорости
        description="Размер контекста (уменьшен для скорости)"
    )
    N_GPU_LAYERS: int = Field(
        default=-1,
        description="Количество слоев на GPU (-1 = все слои на GPU)"
    )
    N_THREADS: int = Field(
        default_factory=lambda: get_cpu_info()[2],  # Автоматически определяем оптимальные потоки
        description="Количество потоков CPU (автоматически = физические ядра)"
    )
    N_THREADS_BATCH: int = Field(
        default_factory=lambda: max(1, get_cpu_info()[2] // 2),  # Половина от физических ядер
        description="Потоки для батчинга (автоматически оптимизировано)"
    )
    N_BATCH: int = Field(
        default_factory=lambda: min(128, get_optimal_batch_size()),  # Ограничиваем для скорости
        description="Размер батча (ограничен для скорости)"
    )
    
    # Дополнительные оптимизации GPU
    F16_KV: bool = Field(
        default=True,
        description="Использовать float16 для KV cache (экономия памяти)"
    )
    MUL_MAT_Q: bool = Field(
        default=True,
        description="Матричные операции на GPU"
    )
    USE_MMAP: bool = Field(
        default=True,
        description="Использовать memory mapping"
    )
    USE_MLOCK: bool = Field(
        default=False,
        description="Отключить mlock для экономии памяти"
    )
    VERBOSE: bool = Field(
        default=False,
        description="Отключить verbose для увеличения скорости"
    )
    OFFLOAD_KQV: bool = Field(
        default=True,
        description="Выгружать KQV на GPU"
    )
    NUMA: bool = Field(
        default=False,
        description="Отключить NUMA для стабильности"
    )
    
    # ДОПОЛНИТЕЛЬНЫЕ ОПТИМИЗАЦИИ ДЛЯ СКОРОСТИ
    N_KEEP: int = Field(
        default=0,
        description="Не сохранять токены (экономия памяти)"
    )
    N_DRAFT: int = Field(
        default=0,
        description="Отключить draft sampling"
    )
    N_CHUNKS: int = Field(
        default=1,
        description="Один чанк для скорости"
    )
    N_PARALLEL: int = Field(
        default=1,
        description="Один поток для стабильности"
    )
    VOCAB_ONLY: bool = Field(
        default=False,
        description="Загружать полную модель"
    )

    # Параметры генерации по умолчанию (ОПТИМИЗИРОВАНЫ для содержательных ответов)
    DEFAULT_MAX_TOKENS: int = Field(
        default=300,  # Увеличено для содержательных ответов ~200 слов
        description="Максимальное количество токенов (увеличено для содержательных ответов)"
    )
    DEFAULT_TEMPERATURE: float = Field(
        default=0.7,  # Увеличено для более творческих ответов
        description="Температура (увеличена для творческих ответов)"
    )
    DEFAULT_TOP_P: float = Field(
        default=0.9,  # Увеличено для разнообразия
        description="Top-p (увеличен для разнообразия)"
    )
    DEFAULT_TOP_K: int = Field(
        default=40,  # Увеличено для разнообразия
        description="Top-k (увеличен для разнообразия)"
    )
    DEFAULT_REPEAT_PENALTY: float = Field(
        default=1.1,  # Увеличено для избежания повторений
        description="Штраф за повторения (увеличен для избежания повторений)"
    )

    # Лимиты (ОПТИМИЗИРОВАНЫ для содержательных ответов)
    MAX_HISTORY_LENGTH: int = Field(
        default=6,  # Увеличено для лучшего контекста
        description="Максимальная длина истории диалога "
        "(увеличена для лучшего контекста)"
    )
    MAX_MESSAGE_LENGTH: int = Field(
        default=200,  # Увеличено для длинных сообщений
        description="Максимальная длина сообщения (увеличена для длинных сообщений)"
    )
    MAX_CHARACTER_NAME_LENGTH: int = Field(
        default=15,
        description="Максимальная длина имени персонажа"
    )
    MAX_RESPONSE_LENGTH: int = Field(
        default=400,  # Увеличено для содержательных ответов ~200 слов
        description="Максимальная длина ответа в символах (увеличено для содержательных ответов)"
    )

    # Настройки безопасности
    ENABLE_CONTENT_FILTER: bool = Field(
        default=False,
        description="Включить фильтрацию контента (отключено для NSFW)"
    )
    FORBIDDEN_WORDS: list = Field(
        default=[],
        description="Запрещенные слова"
    )

    # Настройки логирования (ОПТИМИЗИРОВАНЫ для производительности)
    LOG_CHAT_REQUESTS: bool = Field(
        default=False,  # Отключено для скорости
        description="Логировать запросы чата (отключено для скорости)"
    )
    LOG_CHAT_RESPONSES: bool = Field(
        default=False,
        description="Логировать ответы чата (отключено для скорости)"
    )

    # Настройки производительности (ОПТИМИЗИРОВАНЫ)
    ENABLE_CACHE: bool = Field(
        default=False,  # Отключено для экономии памяти
        description="Включить кэширование (отключено для экономии памяти)"
    )
    CACHE_TTL: int = Field(
        default=300,  # Уменьшено для экономии памяти
        description=(
            "Время жизни кэша "
            "в секундах (уменьшено для экономии памяти)"
        )
    )
    MAX_CACHE_SIZE: int = Field(
        default=50,  # Уменьшено для экономии памяти
        description="Максимальный размер кэша (уменьшен для экономии памяти)"
    )
    
    # Дополнительные настройки производительности
    SEED: int = Field(
        default=42,
        description="Фиксированный seed для воспроизводимости"
    )
    EMBEDDING: bool = Field(
        default=False,
        description="Отключить embedding для экономии ресурсов"
    )
    ROPE_SCALING: Optional[str] = Field(
        default=None,
        description="Отключить rope scaling для стабильности"
    )
    FTYPE: str = Field(
        default="q6_k",
        description="Тип квантизации модели"
    )
    
    # Text Generation WebUI настройки
    TEXTGEN_WEBUI_URL: str = Field(
        default="http://localhost:7860",
        description="URL text-generation-webui API"
    )

    class Config:
        env_prefix = "CHAT_"
        case_sensitive = False


# Создаем экземпляр конфигурации с выводом информации об оптимизации
chat_config = ChatConfig()

# Выводим информацию об оптимизации при загрузке конфигурации
if __name__ == "__main__":
    from app.utils.cpu_utils import print_cpu_optimization_info
    print_cpu_optimization_info()
    print("✅ Конфигурация загружена с оптимальными настройками:")
    print(
        f"  Кoнтекст: {chat_config.N_CTX}"
    )
    print(
        f"  Потоки CPU: {chat_config.N_THREADS} (оптимально!)"
    )
    print(
        f"  Потоки батча: {chat_config.N_THREADS_BATCH}"
    )
    print(
        f"  Батч: {chat_config.N_BATCH} (авто-оптимизирован)"
    )
    print(
        f"  N_GPU_LAYERS: {chat_config.N_GPU_LAYERS}"
    )
    print(f"  N_KEEP: {chat_config.N_KEEP}")
    print(f"  N_DRAFT: {chat_config.N_DRAFT}")
    print(f"  N_CHUNKS: {chat_config.N_CHUNKS}")
    print(f"  N_PARALLEL: {chat_config.N_PARALLEL}")
    print(f"  VOCAB_ONLY: {chat_config.VOCAB_ONLY}")
    print(f"  DEFAULT_MAX_TOKENS: {chat_config.DEFAULT_MAX_TOKENS}")
    print(f"  DEFAULT_TEMPERATURE: {chat_config.DEFAULT_TEMPERATURE}")
    print(f"  DEFAULT_TOP_P: {chat_config.DEFAULT_TOP_P}")
    print(f"  DEFAULT_TOP_K: {chat_config.DEFAULT_TOP_K}")
    print(f"  DEFAULT_REPEAT_PENALTY: {chat_config.DEFAULT_REPEAT_PENALTY}")
    print(f"  MAX_HISTORY_LENGTH: {chat_config.MAX_HISTORY_LENGTH}")
    print(f"  MAX_MESSAGE_LENGTH: {chat_config.MAX_MESSAGE_LENGTH}")
    print(f"  MAX_CHARACTER_NAME_LENGTH: {chat_config.MAX_CHARACTER_NAME_LENGTH}")
    print(f"  MAX_RESPONSE_LENGTH: {chat_config.MAX_RESPONSE_LENGTH}")
    print(f"  ENABLE_CONTENT_FILTER: {chat_config.ENABLE_CONTENT_FILTER}")
    print(f"  FORBIDDEN_WORDS: {chat_config.FORBIDDEN_WORDS}")
    print(f"  LOG_CHAT_REQUESTS: {chat_config.LOG_CHAT_REQUESTS}")
    print(f"  LOG_CHAT_RESPONSES: {chat_config.LOG_CHAT_RESPONSES}")
    print(f"  ENABLE_CACHE: {chat_config.ENABLE_CACHE}")
    print(f"  CACHE_TTL: {chat_config.CACHE_TTL}")
    print(f"  MAX_CACHE_SIZE: {chat_config.MAX_CACHE_SIZE}")
    print(f"  SEED: {chat_config.SEED}")
    print(f"  EMBEDDING: {chat_config.EMBEDDING}")
    print(f"  ROPE_SCALING: {chat_config.ROPE_SCALING}")
    print(f"  FTYPE: {chat_config.FTYPE}")
    print(f"  TEXTGEN_WEBUI_URL: {chat_config.TEXTGEN_WEBUI_URL}")

# Экспортируем URL для использования в других модулях
TEXTGEN_WEBUI_URL = chat_config.TEXTGEN_WEBUI_URL
LLAMA_API_URL: str = os.getenv("LLAMA_API_URL", "http://localhost:8000") 