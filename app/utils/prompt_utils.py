"""
Утилиты для работы с промптами.
"""
from typing import List, Optional
from app.config.default_prompts import (
    DEFAULT_POSITIVE_PROMPTS,
    DEFAULT_NEGATIVE_PROMPTS
)

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

def combine_prompts(
    user_prompt: str,
    default_prompts: Optional[str] = None,
    weight: float = 1.0
) -> str:
    """
    Комбинирует пользовательский промпт с дефолтными промптами.
    
    Args:
        user_prompt: Пользовательский промпт
        default_prompts: Дефолтные промпты (если None, используются стандартные)
        weight: Вес дефолтных промптов (1.0 = полный вес)
        
    Returns:
        str: Комбинированный промпт
    """
    if not default_prompts:
        return user_prompt
        
    if weight <= 0:
        return user_prompt
        
    if weight >= 1:
        return f"{user_prompt}, {default_prompts}"
        
    # Если вес меньше 1, добавляем дефолтные промпты с меньшим приоритетом
    return f"{user_prompt}, ({default_prompts}:{weight})"

def format_prompt(prompt: str) -> str:
    """
    Форматирует промпт, удаляя лишние пробелы и запятые.
    
    Args:
        prompt: Исходный промпт
        
    Returns:
        str: Отформатированный промпт
    """
    # Разбиваем на части по запятым
    parts = [p.strip() for p in prompt.split(",")]
    
    # Удаляем пустые части
    parts = [p for p in parts if p]
    
    # Собираем обратно
    return ", ".join(parts) 