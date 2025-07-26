"""
Модуль с дефолтными промптами для улучшения качества генерации.
ИСПРАВЛЕНО: Убраны противоречивые промпты, добавлены промпты против коллажей
"""

DEFAULT_POSITIVE_PROMPTS = [
    "photorealistic",
    "hyperrealistic",
    "masterpiece",
    "best quality",
    "8K",
    "high resolution",
    "DSLR photo",
    "full body shot",
    "full body portrait",
    "realistic skin",
    "beautiful face",
    "detailed face",
    "frontal face",
    "natural pose",
    "NSFW",
    "perfect proportions",
    "good anatomy"
]

DEFAULT_NEGATIVE_PROMPTS = [
    "(deformed iris, deformed pupils, semi-realistic, cgi, 3d, render, sketch, cartoon, drawing, anime)",
    "text",
    "cropped",
    "out of frame",
    "worst quality",
    "low quality",
    "jpeg artifacts",
    "ugly",
    "duplicate",
    "morbid",
    "mutilated",
    "extra fingers",
    "mutated hands",
    "poorly drawn hands",
    "poorly drawn face",
    "mutation",
    "deformed",
    "blurry",
    "dehydrated",
    "bad anatomy",
    "bad proportions",
    "extra limbs",
    "cloned face",
    "disfigured",
    "gross proportions",
    "malformed limbs",
    "missing arms",
    "missing legs",
    "extra arms",
    "extra legs",
    "fused fingers",
    "too many fingers",
    "long neck",
    "UnrealisticDream",
    "(deformed iris, deformed pupils, semi-realistic, cgi, 3d, render, sketch, cartoon, drawing, anime, mutated hands and fingers:1.4)",
    "(deformed, distorted, disfigured:1.3)",
    "poorly drawn",
    "wrong anatomy",
    "floating limbs",
    "disconnected limbs",
    "mutated",
    "disgusting",
    "amputation"
]

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