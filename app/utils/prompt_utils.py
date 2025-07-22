"""
Utilities for working with prompts.
"""
from typing import Optional

import sys
from pathlib import Path

# Добавляем корень проекта в путь для импорта
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app.config.shared_prompts import (
    get_default_positive_prompts,
    get_default_negative_prompts,
    get_adetailer_positive_prompts,
    get_adetailer_negative_prompts
)


def get_default_positive_prompts_str() -> str:
    """
    Get a string with default positive prompts.
    
    Returns:
        str: String with default positive prompts separated by commas
    """
    return get_default_positive_prompts()


def get_default_negative_prompts_str() -> str:
    """
    Get a string with default negative prompts.
    
    Returns:
        str: String with default negative prompts separated by commas
    """
    return get_default_negative_prompts()


def combine_prompts(user_prompt: str,
                   default_positive: Optional[str] = None,
                   default_negative: Optional[str] = None) -> tuple[str, str]:
    """
    Combines user prompt with default prompts.
    
    Args:
        user_prompt: User prompt
        default_positive: Default positive prompts
        default_negative: Default negative prompts
        
    Returns:
        tuple: (combined_positive, combined_negative)
    """
    if default_positive is None:
        default_positive = get_default_positive_prompts_str()
    
    if default_negative is None:
        default_negative = get_default_negative_prompts_str()
    
    combined_positive = f"{user_prompt}, {default_positive}"
    combined_negative = default_negative
    
    return combined_positive, combined_negative 