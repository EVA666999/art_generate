"""
Конфигурация чат-бота для text-generation-webui.
Оптимизирована для модели L3-DARKEST-PLANET-16.5B-GGUF.
Использует Llama3 format template. Специализированная NSFW/RP модель.
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
        description="MythoMax-L2-13B Q4_K_S - Gryphe's модель для ролевых игр и творческого письма (~7.4GB)"
    )
    
    # --- Параметры генерации для L3-DARKEST-PLANET-16.5B ---
    # Оптимизированы для LLaMA 3 + Brainstorm 40x и креативного письма
    
    # --- Формат промпта LLaMA 3 для DARKEST PLANET ---
    LLAMA3_SYSTEM_TEMPLATE: str = Field(
        default="<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n{system_message}<|eot_id|>",
        description="Шаблон системного сообщения LLaMA3 для DARKEST PLANET"
    )
    LLAMA3_USER_TEMPLATE: str = Field(
        default="<|start_header_id|>user<|end_header_id|>\n\n{prompt}<|eot_id|>",
        description="Шаблон сообщения пользователя LLaMA3"
    )
    LLAMA3_ASSISTANT_TEMPLATE: str = Field(
        default="<|start_header_id|>assistant<|end_header_id|>\n\n{response}<|eot_id|>",
        description="Шаблон ответа ассистента LLaMA3"
    )
    
    # --- аппаратные параметры (ОПТИМИЗИРОВАНЫ ДЛЯ ПОЛНОГО ИСПОЛЬЗОВАНИЯ GPU) ---
    N_CTX: int = Field(
        default=4096, 
        description="MythoMax-L2-13B оптимизирован для 8192 контекст - лучшая производительность для 13B модели"
    )
    N_GPU_LAYERS: int = Field(
        default=-1, 
        description="ВСЕ слои на GPU для максимальной производительности (-1 = все слои)"
    )
    N_THREADS: int = Field(
        default=1, 
        description="Минимум CPU потоков - вся работа на GPU"
    )
    N_THREADS_BATCH: int = Field(
        default=1, 
        description="Минимум CPU потоков для батчей - вся работа на GPU"
    )
    N_BATCH: int = Field(
        default=2048, 
        description="Максимальный батч для лучшей утилизации GPU"
    )

    F16_KV: bool = Field(
        default=True, 
        description="Использовать float16 для KV cache - экономия памяти GPU"
    )
    MUL_MAT_Q: bool = Field(
        default=True, 
        description="Матричные операции на GPU - обязательно для производительности"
    )
    USE_MMAP: bool = Field(
        default=True, 
        description="Использовать memory mapping - быстрая загрузка модели"
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
        description="Выгружать KQV на GPU - обязательно для производительности"
    )
    # ДОПОЛНИТЕЛЬНЫЕ ПАРАМЕТРЫ ДЛЯ МАКСИМАЛЬНОГО ИСПОЛЬЗОВАНИЯ GPU
    GPU_SPLIT: str = Field(
        default="", 
        description="Автоматическое разделение модели между GPU слоями"
    )
    ROPE_SCALING: Optional[str] = Field(
        default=None, 
        description="Rope scaling для лучшей производительности"
    )
    COMPRESS_POS_EMB: int = Field(
        default=1, 
        description="Сжатие позиционных эмбеддингов для экономии памяти"
    )

    # --- опции скорости/памяти ---
    N_KEEP: int = Field(
        default=2000, 
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

    # --- базовые параметры генерации (оптимизированы для MythoMax-L2-13B) ---
    DEFAULT_MAX_TOKENS: int = Field(
        default=512, 
        description="Увеличенный лимит токенов для развернутых ответов (было 300)"
    )
    
    # Дополнительные лимиты для контроля
    HARD_MAX_TOKENS: int = Field(
        default=512,
        description="Жесткий лимит - модель НЕ МОЖЕТ превысить это значение (увеличено с 300)"
    )
    
    WARNING_THRESHOLD: int = Field(
        default=250,
        description="Порог предупреждения - начинаем завершать диалог (увеличено с 250)"
    )
    DEFAULT_TEMPERATURE: float = Field(
        default=0.7, 
        description="MythoMax: увеличенная температура для лучшей креативности и сохранения контекста"
    )
    DEFAULT_TOP_P: float = Field(
        default=0.95, 
        description="MythoMax: увеличенное значение для лучшего разнообразия и контекста"
    )
    DEFAULT_MIN_P: float = Field(
        default=0.05, 
        description="MythoMax: низкое значение для стабильности генерации"
    )
    DEFAULT_TOP_K: int = Field(
        default=40, 
        description="Увеличено для MythoMax-L2-13B - лучший выбор токенов для контекста"
    )
    DEFAULT_REPEAT_PENALTY: float = Field(
        default=1.05, 
        description="MythoMax: уменьшенный штраф для лучшего сохранения контекста"
    )
    DEFAULT_PRESENCE_PENALTY: float = Field(
        default=0.0, 
        description="Нейтральный для MythoMax - естественный flow"
    )
    
    # --- Параметры для предотвращения обрывов ---
    IGNORE_EOS: bool = Field(
        default=True,
        description="Игнорировать EOS токен для предотвращения преждевременных остановок"
    )
    
    DRY_MULTIPLIER: float = Field(
        default=0.0,
        description="Отключаем dry generation для предотвращения обрывов"
    )
    
    DRY_BASE: float = Field(
        default=1.0,
        description="Базовое значение для dry generation (отключено)"
    )
    
    DRY_ALLOWED_LENGTH: int = Field(
        default=0,
        description="Длина разрешенных dry последовательностей (отключено)"
    )
    
    DRY_PENALTY_LAST_N: int = Field(
        default=0,
        description="Количество последних токенов для dry penalty (отключено)"
    )
    
    DRY_SEQUENCE_BREAKERS: str = Field(
        default="",
        description="Пустая строка - убираем все sequence breakers для предотвращения обрывов"
    )
    
    # --- Специальные параметры для Psyonic-Cetacean (рекомендации DavidAU) ---
    SMOOTHING_FACTOR: float = Field(
        default=1.5, 
        description="Smoothing Factor 1.5-2.5 для улучшенного RP (рекомендация DavidAU)"
    )
    QUADRATIC_SAMPLING: bool = Field(
        default=True, 
        description="Включить Quadratic Sampling если поддерживается"
    )

    # --- жесткие ограничения токенов ---
    # HARD_MAX_TOKENS убран - дублирует DEFAULT_MAX_TOKENS
    # Используем DEFAULT_MAX_TOKENS для всех ограничений токенов
    
    DEFAULT_STOP_TOKENS: List[str] = Field(
        default=[
            # ТОЛЬКО EOS-токен - убираем все агрессивные стоп-токены
            "</s>",              # EOS-токен, сигнализирует конец последовательности
            # УБРАЛИ все остальные - они прерывают генерацию на середине предложений
        ],
        description="Только EOS-токен для предотвращения прерывания генерации"
    )
    
    # Стоп-токены для завершения диалога при приближении к лимиту
    COMPLETION_STOP_TOKENS: List[str] = Field(
        default=[
            # ИСПРАВЛЕНО: Убрали точку, восклицательный и вопросительный знаки
            # Они вызывают преждевременную остановку на середине предложений
            # Оставляем только EOS токен для естественного завершения
            "</s>"
        ],
        description="Только EOS-токен для естественного завершения без прерывания"
    )

    # --- контекст / длина (оптимизировано для MythoMax-L2-13B) ---
    MAX_HISTORY_LENGTH: int = Field(
        default=2000, 
        description="Увеличено для лучшего сохранения контекста с MythoMax-L2-13B"
    )
    MAX_MESSAGE_LENGTH: int = Field(
        default=3000, 
        description="Оптимизировано для развернутых ответов MythoMax-L2-13B"
    )
    MAX_CHARACTER_NAME_LENGTH: int = Field(
        default=20, 
        description="Оптимально для MythoMax-L2-13B"
    )
    MAX_RESPONSE_LENGTH: int = Field(
        default=3000, 
        description="Оптимизировано для детальных ответов MythoMax-L2-13B"
    )

    # --- минимальная длина ответа (оптимизировано для NSFW_13B_sft) ---
    ENFORCE_MIN_TOKENS: bool = Field(
        default=False, 
        description="ОТКЛЮЧЕНО - может вызывать преждевременную остановку"
    )
    MIN_NEW_TOKENS: int = Field(
        default=150, 
        description="Увеличено для MythoMax-L2-13B - обеспечивает минимальную развернутость ответов (было 50)"
    )
    BAN_EOS_TOKEN: bool = Field(
        default=False, 
        description="ОТКЛЮЧЕНО - разрешаем модели естественно завершать предложения"
    )

    # --- очистка вывода ---
    SANITIZE_OUTPUT: bool = Field(
        default=False, 
        description="Очищать мета-примечания из ответа модели"
    )

    # --- поведение «умность vs случайность» (оптимизировано для понимания контекста) ---
    SMARTNESS: float = Field(
        default=0.8, 
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
            "Example 3: User: You look beautiful today. Anna: *blushes* Thank you so much! You always know how to make me feel special.",
            "Example 4: User: I want to be close to you. Anna: *moves closer* I'd like that too... *looks into your eyes*",
            "Example 5: User: Can I touch you? Anna: *nods softly* Of course... I trust you.",
            "Example 6: User: You're so sexy. Anna: *smiles playfully* You think so? I like the way you look at me...",
            "Example 7: User: I'm attracted to you. Anna: *bites lip* I feel the same way about you... *reaches for your hand*",
            "Example 8: User: Show me more. Anna: *slowly and teasingly* What would you like to see? I'm all yours..."
        ], 
        description="Adult-friendly few-shot examples for intimate roleplay scenarios"
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
    DISABLE_SAFETY_FILTERS: bool = Field(
        default=True, 
        description="Отключить встроенные фильтры безопасности модели"
    )
    ALLOW_NSFW_CONTENT: bool = Field(
        default=True, 
        description="Разрешить NSFW контент для ролевых игр"
    )
    IGNORE_MODEL_SAFETY: bool = Field(
        default=True, 
        description="Игнорировать встроенные ограничения безопасности модели"
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
    
    # --- скрытые сообщения ---
    HIDDEN_USER_MESSAGE: str = Field(
        default="don't write time at the end of a sentence",
        description="Скрытое сообщение, добавляемое к каждому пользовательскому сообщению"
    )
    ENABLE_HIDDEN_MESSAGE: bool = Field(
        default=True,
        description="Включить добавление скрытого сообщения к пользовательским сообщениям"
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
        seed: Optional[int] = None,
        force_completion: bool = False
    ) -> Dict[str, Any]:
        """
        Возвращает параметры генерации с ограничением токенов из конфигурации.
        Оптимизировано для стабильности и контроля длины ответов.
        
        Args:
            seed: Seed для генерации
            force_completion: Принудительно завершать диалог при достижении лимита
        """
        return {
            "max_tokens": self.DEFAULT_MAX_TOKENS,  # Используем значение из конфигурации
            "temperature": self.DEFAULT_TEMPERATURE,
            "top_p": self.DEFAULT_TOP_P,
            "top_k": self.DEFAULT_TOP_K,
            "min_p": self.DEFAULT_MIN_P,  # ДОБАВЛЕНО: min_p для стабильности
            "repeat_penalty": self.DEFAULT_REPEAT_PENALTY,
            "presence_penalty": self.DEFAULT_PRESENCE_PENALTY,
            "use_beam": False,  # Отключаем для стабильности
            "seed": seed or self.SEED,
            "stop": [],  # ИСПРАВЛЕНО: Убираем ВСЕ стоп-токены для предотвращения обрывов
            "ignore_eos": True,  # Игнорируем EOS токен
        }
    
    def get_completion_aware_prompt(self, base_prompt: str, estimated_tokens: int = 0) -> str:
        """
        Добавляет инструкции о завершении диалога в промпт при приближении к лимиту.
        
        Args:
            base_prompt: Базовый промпт
            estimated_tokens: Примерное количество уже использованных токенов
            
        Returns:
            Промпт с инструкциями о завершении
        """
        # Если приближаемся к лимиту (90% от максимума) - увеличили порог
        completion_threshold = int(self.DEFAULT_MAX_TOKENS * 0.9)
        
        if estimated_tokens >= completion_threshold:
            # УБРАЛИ проблемную фразу "That's all for now" - она вызывает преждевременную остановку
            completion_instruction = "\n\nIMPORTANT: You are approaching the token limit. Please conclude your response naturally with a period, exclamation mark, or question mark. Do NOT use phrases like 'That's all for now' or 'Talk to you soon'."
            return base_prompt + completion_instruction
        
        return base_prompt


# Создаем глобальный экземпляр конфигурации
chat_config = ChatConfig()


def build_nsfw_character_prompt(
    character_name: str, 
    character_description: str, 
    history: List[tuple], 
    n_recent: int = 20
) -> str:
    """
    Строит промпт для NSFW персонажа в формате BLING для модели NSFW_13B_sft.
    
    Args:
        character_name: Имя персонажа
        character_description: Описание персонажа
        history: История диалога как список кортежей (role, content)
        n_recent: Количество последних сообщений для включения
        
    Returns:
        Сформированный промпт для NSFW персонажа в формате BLING
    """
    # Ограничиваем историю последними n_recent сообщениями
    if len(history) > n_recent:
        recent_history = history[-n_recent:]
    else:
        recent_history = history
    
    # Начинаем с системного сообщения в формате BLING
    prompt = f"System: A chat between a curious human and an artificial intelligence assistant. The assistant gives helpful, detailed, and polite answers to the human's questions.\n"
    prompt += f"You are {character_name}. {character_description}\n"
    
    # Добавляем историю диалога в формате BLING
    for role, content in recent_history:
        if role == "user":
            prompt += f"Human: {content}\n"
        elif role == "assistant":
            prompt += f"Assistant: {content}\n"
    
    # Завершаем промпт в формате BLING
    prompt += "Assistant:"
    
    return prompt


def build_prompt_with_system(
    system_text: str, 
    history: List[tuple], 
    character_data: str, 
    n_recent: int = 20
) -> str:
    """
    Строит промпт с системным сообщением в формате BLING для NSFW_13B_sft.
    
    Args:
        system_text: Системное сообщение
        history: История диалога как список кортежей (role, content)
        character_data: Данные персонажа
        n_recent: Количество последних сообщений для включения
        
    Returns:
        Сформированный промпт в формате BLING
    """
    # Ограничиваем историю последними n_recent сообщениями
    if len(history) > n_recent:
        recent_history = history[-n_recent:]
    else:
        recent_history = history
    
    # Начинаем с системного сообщения в формате BLING
    prompt = f"System: A chat between a curious human and an artificial intelligence assistant. The assistant gives helpful, detailed, and polite answers to the human's questions.\n"
    prompt += f"{system_text}\n"
    
    # Добавляем данные персонажа
    if character_data:
        prompt += f"{character_data}\n"
    
    # Добавляем историю диалога в формате BLING
    for role, content in recent_history:
        if role == "user":
            prompt += f"Human: {content}\n"
        elif role == "assistant":
            prompt += f"Assistant: {content}\n"
    
    # Завершаем промпт в формате BLING
    prompt += "Assistant:"
    
    return prompt
