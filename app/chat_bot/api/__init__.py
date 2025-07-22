"""
API эндпоинты чат-бота.
"""

from .chat_endpoints import router as chat_router
from .character_endpoints import router as character_router
 
__all__ = ["chat_router", "character_router"] 