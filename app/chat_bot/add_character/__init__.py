"""
Система добавления персонажей.
"""

from .character_registry import (
    get_character_registry,
    get_character_data,
    get_all_characters,
    reload_characters
)

from .character_api import router as character_router
from .universal_chat_api import router as universal_chat_router

__all__ = [
    "get_character_registry",
    "get_character_data", 
    "get_all_characters",
    "reload_characters",
    "character_router",
    "universal_chat_router"
]
