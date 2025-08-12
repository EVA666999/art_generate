"""
Модуль с дефолтными промптами для улучшения качества генерации.
ИСПРАВЛЕНО: Убраны противоречивые промпты, добавлены промпты против коллажей
"""

DEFAULT_POSITIVE_PROMPTS = [
    "1girl",
    "solo",
    "anime realism", 
    "realistic anime",
    "high quality anime", 
    "large expressive eyes", 
    "clean lines", 
    "smooth skin", 
    "perfect hands", 
    "full body", 
    "nipples",
    "realistic shadows", 
    "high quality shadows",
    "realistic lighting",
    "detailed realistic hair",
    "detailed realistic background",
    "detailed realistic face",
    "detailed realistic body",
    "detailed realistic hands",
    "detailed realistic feet",
    "detailed realistic legs",
    "detailed realistic tits",
    'realistic background',
]

DEFAULT_NEGATIVE_PROMPTS = [
    "low quality", 
    "blurry", 
    "jpeg artifacts", 
    "extra fingers", 
    "mutated hands", 
    "bad anatomy", 
    "flat colors",
    "black and white",
    "worst quality:1.6", 
    "low quality:1.6", 
    "zombie", 
    "sketch", 
    "interlocked fingers",
]
# Дополнительные промпты для конкретных ситуаций


# Функция для получения промптов
def get_default_positive_prompts() -> str:
    """Возвращает строку с дефолтными позитивными промптами"""
    return ", ".join(DEFAULT_POSITIVE_PROMPTS)

def get_default_negative_prompts() -> str:
    """Возвращает строку с дефолтными негативными промптами"""
    return ", ".join(DEFAULT_NEGATIVE_PROMPTS)

def get_enhanced_prompts(base_prompt: str, use_defaults: bool = True) -> tuple[str, str]:
    """
    Улучшает базовый промпт, добавляя дефолтные промпты
    
    Args:
        base_prompt: Базовый промпт пользователя
        use_defaults: Использовать ли дефолтные промпты
        
    Returns:
        tuple: (enhanced_positive, enhanced_negative)
    """
    if not use_defaults:
        return base_prompt, ""
    
    # Добавляем дефолтные промпты к базовому
    enhanced_positive = f"{get_default_positive_prompts()}, {base_prompt}"
    enhanced_negative = get_default_negative_prompts()
    
    return enhanced_positive, enhanced_negative 