"""
Модуль с дефолтными промптами для улучшения качества генерации.
Эти промпты будут автоматически добавляться к каждому запросу пользователя.
Настроены для генерации целого тела с лицом. 
Оптимизированы для баланса качества и количества.
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
    "complete body",
    "head to toe",
    "soft lighting",
    "sharp focus",
    "realistic skin",
    "beautiful face",
    "detailed face",
    "frontal face",
    "looking at viewer",
    "natural pose",
    "beautiful model",
    "seductive",
    "sexy",
    "lingerie",
    "nude",
    "single portrait, one person, centered, no split, no collage, "
    "no two people, no double, no split image",
    "NSFW",
    "perfect proportions",
    "good anatomy"
]

DEFAULT_NEGATIVE_PROMPTS = [
    "lowres",
    "blurry",
    "worst quality",
    "low quality",
    "text",
    "watermark",
    "signature",
    "cropped",
    "out of frame",
    "partial body",
    "body cut off",
    "head cut off",
    "close-up",
    "face only",
    "head only",
    "bust shot",
    "upper body only",
    "back view",
    "from behind",
    "error",
    "jpeg artifacts",
    "bad anatomy",
    "bad proportions",
    "mutated hands",
    "extra limbs",
    "missing limbs",
    "deformed",
    "cartoon",
    "anime",
    "CGI",
    "3D",
    "render",
    "sketch",
    "drawing",
    "ugly",
    "oversaturated",
    "monochrome"
]


def get_default_positive_prompts() -> str:
    """
    Получить строку с дефолтными позитивными промптами.
    
    Returns:
        str: Строка с дефолтными позитивными промптами, разделенными запятыми
    """
    return ", ".join(DEFAULT_POSITIVE_PROMPTS)


def get_default_negative_prompts() -> str:
    """
    Получить строку с дефолтными негативными промптами.
    
    Returns:
        str: Строка с дефолтными негативными промптами, разделенными запятыми
    """
    return ", ".join(DEFAULT_NEGATIVE_PROMPTS) 