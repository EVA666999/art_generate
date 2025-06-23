"""
Модуль с дефолтными промптами для улучшения качества генерации.
Эти промпты будут автоматически добавляться к каждому запросу пользователя.
"""

DEFAULT_POSITIVE_PROMPTS = [
    "photorealistic",
    "hyperrealistic",
    "ultra-detailed",
    "masterpiece",
    "best quality",
    "8K",
    "high resolution",
    "DSLR photo",
    "analog photo",
    "portrait photography",
    "soft lighting",
    "sharp focus",
    "realistic skin",
    "realistic eyes",
    "symmetrical face",
    "perfect face",
    "close-up face",
    "face in frame",
    "frontal face",
    "looking at viewer",
    "eye contact",
    "natural pose",
    "beautiful model",
    "seductive",
    "sensual",
    "erotic",
    "sexy",
    "lingerie",
    "nude",
    "NSFW"
]



DEFAULT_NEGATIVE_PROMPTS = [
    "lowres",
    "blurry",
    "worst quality",
    "low quality",
    "text",
    "watermark",
    "signature",
    "duplicate",
    "cropped",
    "out of frame",
    "partial face",
    "face obscured",
    "looking away",
    "back view",
    "from behind",
    "error",
    "jpeg artifacts",
    "bad anatomy",
    "bad proportions",
    "mutated hands",
    "fused fingers",
    "extra limbs",
    "missing limbs",
    "disfigured",
    "deformed",
    "poorly drawn face",
    "cartoon",
    "anime",
    "CGI",
    "3D",
    "render",
    "sketch",
    "drawing",
    "doll",
    "stupid",
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