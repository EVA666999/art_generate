"""
Конфигурация для чат-бота с настраиваемым характером.
Оптимизирована для модели MythoMax L2 13B GGUF.
(и совместима с локальными backends: llama.cpp, ctransformers)
"""
from typing import Optional, List, Dict, Any
from pydantic_settings import BaseSettings
from pydantic import Field
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()


class ChatConfig(BaseSettings):
    """Конфигурация для чат-бота."""

    # --- Настройки text-generation-webui API ---
    TEXTGEN_WEBUI_ENABLED: bool = Field(
        default=True, 
        description="Включить text-generation-webui API"
    )
    TEXTGEN_WEBUI_URL: str = Field(
        default="http://localhost:5000", 
        description="URL text-generation-webui API"
    )
    TEXTGEN_WEBUI_TIMEOUT: int = Field(
        default=300, 
        description="Таймаут для API запросов в секундах"
    )
    TEXTGEN_WEBUI_MODEL: str = Field(
        default="Gryphe-MythoMax-L2-13b.Q4_K_S.gguf", 
        description="Название модели для загрузки"
    )
    
    # --- Параметры генерации для MythoMax L2 13B ---
    # Используем единые параметры DEFAULT_* вместо дублирования
    
    # --- Формат промпта для MythoMax (Alpaca) ---
    MYTHOMAX_SYSTEM_TEMPLATE: str = Field(
        default="{system_message}",
        description="Шаблон системного сообщения для MythoMax"
    )
    MYTHOMAX_INSTRUCTION_TEMPLATE: str = Field(
        default="### Instruction:\n{prompt}",
        description="Шаблон инструкции для MythoMax"
    )
    MYTHOMAX_RESPONSE_TEMPLATE: str = Field(
        default="### Response:\n",
        description="Шаблон ответа для MythoMax"
    )
    
    # --- аппаратные параметры (оптимизированы для качества) ---
    N_CTX: int = Field(
        default=4096, 
        description="Размер контекста увеличен для лучшего понимания"
    )
    N_GPU_LAYERS: int = Field(
        default=-1, 
        description="Количество слоев на GPU (-1 = все слои на GPU)"
    )
    N_THREADS: int = Field(
        default=16, 
        description="Количество потоков CPU (увеличено для качества)"
    )
    N_THREADS_BATCH: int = Field(
        default=8, 
        description="Потоки для батчинга (оптимизировано для качества)"
    )
    N_BATCH: int = Field(
        default=128, 
        description="Размер батча увеличен для лучшего качества"
    )

    F16_KV: bool = Field(
        default=True, 
        description="Использовать float16 для KV cache"
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

    # --- опции скорости/памяти ---
    N_KEEP: int = Field(
        default=300, 
        description="Не сохранять токены (экономия памяти)"
    )
    N_DRAFT: int = Field(
        default=6, 
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

    # --- базовые параметры генерации (оптимизированы для понимания контекста) ---
    DEFAULT_MAX_TOKENS: int = Field(
        default=300, 
        description="Макс. токены для генерации (увеличено для лучшего контекста)"
    )
    DEFAULT_TEMPERATURE: float = Field(
        default=0.8, 
        description="Температура увеличена для лучшего понимания контекста"
    )
    DEFAULT_TOP_P: float = Field(
        default=0.85, 
        description="Top-p увеличен для лучшего понимания контекста"
    )
    DEFAULT_TOP_K: int = Field(
        default=50, 
        description="Top-k увеличен для лучшего выбора токенов в контексте"
    )
    DEFAULT_REPEAT_PENALTY: float = Field(
        default=1.15, 
        description="Штраф за повторения увеличен для лучшего качества контекста"
    )
    DEFAULT_PRESENCE_PENALTY: float = Field(
        default=0.2, 
        description="Presence penalty увеличен для лучшего разнообразия в контексте"
    )

    # --- жесткие ограничения токенов ---
    # HARD_MAX_TOKENS убран - дублирует DEFAULT_MAX_TOKENS
    # Используем DEFAULT_MAX_TOKENS для всех ограничений токенов
    
    DEFAULT_STOP_TOKENS: List[str] = Field(
        default=[
            "<|im_end|>", "<|endoftext|>", "<|im_start|>", 
            "###", "Human:", "Assistant:"
        ], 
        description="Расширенные токены остановки для MythoMax"
    )

    # --- контекст / длина (оптимизировано для понимания контекста) ---
    MAX_HISTORY_LENGTH: int = Field(
        default=25, 
        description="Макс. длина истории диалога (увеличена для лучшего понимания контекста)"
    )
    MAX_MESSAGE_LENGTH: int = Field(
        default=800, 
        description="Макс. длина сообщения (увеличена для лучшего понимания деталей)"
    )
    MAX_CHARACTER_NAME_LENGTH: int = Field(
        default=25, 
        description="Макс. длина имени персонажа (увеличена для лучшего понимания)"
    )
    MAX_RESPONSE_LENGTH: int = Field(
        default=1000, 
        description="Макс. длина ответа в символах (увеличена для лучшего понимания контекста)"
    )

    # --- минимальная длина ответа (оптимизировано для понимания контекста) ---
    ENFORCE_MIN_TOKENS: bool = Field(
        default=True, 
        description="Включить принудительную минимальную длину для лучшего понимания контекста"
    )
    MIN_NEW_TOKENS: int = Field(
        default=80, 
        description="Мин. число новых токенов в ответе (увеличено для лучшего понимания контекста)"
    )
    BAN_EOS_TOKEN: bool = Field(
        default=False, 
        description="Разрешить EOS для естественного завершения, но с учетом контекста"
    )

    # --- очистка вывода ---
    SANITIZE_OUTPUT: bool = Field(
        default=False, 
        description="Очищать мета-примечания из ответа модели"
    )

    # --- поведение «умность vs случайность» (оптимизировано для понимания контекста) ---
    SMARTNESS: float = Field(
        default=0.9, 
        description="Баланс умности (увеличен для лучшего понимания контекста)"
    )
    DYNAMIC_SAMPLING: bool = Field(
        default=True, 
        description="Включить адаптивную стратегию для лучшего понимания контекста"
    )
    TEMP_VARIANCE: float = Field(
        default=0.15, 
        description="Вариации температуры для лучшей адаптации к контексту"
    )
    TOP_P_VARIANCE: float = Field(
        default=0.08, 
        description="Вариации top_p для лучшей адаптации к контексту"
    )
    OCCASIONAL_BEAM_PROB: float = Field(
        default=0.15, 
        description="Увеличена вероятность beam search для сложных контекстных ответов"
    )
    ENABLE_COT: bool = Field(
        default=True, 
        description="Включить chain-of-thought для лучшего понимания контекста"
    )
    FEW_SHOT_EXAMPLES: List[str] = Field(
        default=[
            "Example 1: User: How are you? Anna: I'm doing great, thank you! How about you?",
            "Example 2: User: What's new? Anna: Lots of interesting things! I'd love to tell you more if you're interested.",
            "Example 3: User: Remember when we talked about that movie? Anna: Yes, absolutely! We were discussing 'The Matrix'. What specifically interests you about it?",
            "Example 4: User: Let's continue our conversation. Anna: Of course! We stopped when you were telling me about your project. Please go on!",
            "Example 5: User: You're so beautiful. Anna: Thank you for the compliment! I appreciate your kind words. What would you like to talk about?",
            "Example 6: User: I want to kiss you. Anna: I understand your feelings, but let's keep our conversation friendly and respectful. What's on your mind?",
            "Example 7: User: Tell me something sexy. Anna: I'd prefer to keep our conversation appropriate and engaging. What topic would you like to discuss?",
            "Example 8: User: You're making me hot. Anna: Let's focus on having a meaningful conversation instead. What interests you today?"
        ], 
        description="NSFW-aware few-shot examples in English for better context understanding and appropriate responses"
    )

    # --- safety & nsfw ---
    ENABLE_CONTENT_FILTER: bool = Field(
        default=False, 
        description="Включить фильтрацию контента"
    )
    FORBIDDEN_WORDS: List[str] = Field(
        default=[], 
        description="Запрещенные слова"
    )

    # --- логирование и кэш ---
    LOG_CHAT_REQUESTS: bool = Field(
        default=True, 
        description="Логировать запросы чата"
    )
    LOG_CHAT_RESPONSES: bool = Field(
        default=False, 
        description="Логировать ответы чата"
    )
    ENABLE_CACHE: bool = Field(
        default=False, 
        description="Включить кэширование"
    )
    CACHE_TTL: int = Field(
        default=300, 
        description="Время жизни кэша в секундах"
    )
    MAX_CACHE_SIZE: int = Field(
        default=50, 
        description="Максимальный размер кэша"
    )

    # --- настройки стриминга ---
    STREAMING_DELAY_MS: int = Field(
        default=5,
        description="Задержка между чанками стриминга в мс (0 = без задержки)"
    )
    
    # --- прочее ---
    SEED: int = Field(
        default=-1, 
        description="Seed для генерации (42 = стабильный, -1 = случайный)"
    )
    EMBEDDING: bool = Field(
        default=False, 
        description="Отключить embedding для экономии ресурсов"
    )
    ROPE_SCALING: Optional[str] = Field(
        default=None, 
        description="Rope scaling (если требуется)"
    )
    FTYPE: str = Field(
        default="q6_k", 
        description="Тип квантизации модели"
    )

    class Config:
        env_prefix = "CHAT_"
        case_sensitive = False
        protected_namespaces = ()

    # ----------------- helper utilities -----------------
    
    def sample_generation_params(
        self, 
        seed: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Возвращает параметры генерации с ограничением токенов из конфигурации.
        Оптимизировано для стабильности и контроля длины ответов.
        """
        return {
            "max_tokens": self.DEFAULT_MAX_TOKENS,  # Используем значение из конфигурации
            "temperature": self.DEFAULT_TEMPERATURE,
            "top_p": self.DEFAULT_TOP_P,
            "top_k": self.DEFAULT_TOP_K,
            "repeat_penalty": self.DEFAULT_REPEAT_PENALTY,
            "presence_penalty": self.DEFAULT_PRESENCE_PENALTY,
            "use_beam": False,  # Отключаем для стабильности
            "seed": seed or self.SEED,
            "stop": self.DEFAULT_STOP_TOKENS,  # Добавляем стоп-токены
        }


# Создаем глобальный экземпляр конфигурации
chat_config = ChatConfig()


def build_nsfw_character_prompt(
    character_name: str, 
    character_description: str, 
    history: List[tuple], 
    n_recent: int = 20
) -> str:
    """
    Строит промпт для NSFW персонажа с правильным форматированием.
    
    Args:
        character_name: Имя персонажа
        character_description: Описание персонажа
        history: История диалога как список кортежей (role, content)
        n_recent: Количество последних сообщений для включения
        
    Returns:
        Сформированный промпт для NSFW персонажа
    """
    # Ограничиваем историю последними n_recent сообщениями
    if len(history) > n_recent:
        recent_history = history[-n_recent:]
    else:
        recent_history = history
    
    # Начинаем с системного сообщения для NSFW персонажа
    prompt = f"<|im_start|>system\nТы {character_name}. "
    prompt += f"{character_description}\n"
    
    # Добавляем историю диалога
    for role, content in recent_history:
        if role == "user":
            prompt += f"<|im_start|>user\n{content}\n<|im_end|>\n"
        elif role == "assistant":
            prompt += f"<|im_start|>assistant\n{content}\n<|im_end|>\n"
    
    # Завершаем промпт
    prompt += "<|im_start|>assistant\n"
    
    return prompt


def build_prompt_with_system(
    system_text: str, 
    history: List[tuple], 
    character_data: str, 
    n_recent: int = 20
) -> str:
    """
    Строит промпт с системным сообщением и историей диалога.
    
    Args:
        system_text: Системное сообщение
        history: История диалога как список кортежей (role, content)
        character_data: Данные персонажа
        n_recent: Количество последних сообщений для включения
        
    Returns:
        Сформированный промпт
    """
    # Ограничиваем историю последними n_recent сообщениями
    if len(history) > n_recent:
        recent_history = history[-n_recent:]
    else:
        recent_history = history
    
    # Начинаем с системного сообщения
    prompt = f"<|im_start|>system\n{system_text}\n<|im_end|>\n"
    
    # Добавляем данные персонажа
    if character_data:
        prompt += f"<|im_start|>system\n{character_data}\n<|im_end|>\n"
    
    # Добавляем историю диалога
    for role, content in recent_history:
        if role == "user":
            prompt += f"<|im_start|>user\n{content}\n<|im_end|>\n"
        elif role == "assistant":
            prompt += f"<|im_start|>assistant\n{content}\n<|im_end|>\n"
    
    # Завершаем промпт
    prompt += "<|im_start|>assistant\n"
    
    return prompt
