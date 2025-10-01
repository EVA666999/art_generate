"""
API эндпоинты для работы с персонажами.
"""
import logging
from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse

from .character_registry import get_character_registry, get_character_data, get_all_characters, reload_characters

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/characters", tags=["Characters"])


@router.get("/")
async def get_characters():
    """Получает список всех доступных персонажей."""
    try:
        registry = get_character_registry()
        characters = registry.get_character_list()
        
        return JSONResponse(content={
            "characters": characters,
            "total": len(characters),
            "status": "success"
        })
    except Exception as e:
        logger.error(f"[ERROR] Ошибка получения персонажей: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{character_name}")
async def get_character(character_name: str):
    """Получает данные конкретного персонажа."""
    try:
        character_data = get_character_data(character_name)
        
        if not character_data:
            raise HTTPException(
                status_code=404, 
                detail=f"Персонаж '{character_name}' не найден"
            )
        
        return JSONResponse(content={
            "character": character_data,
            "status": "success"
        })
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[ERROR] Ошибка получения персонажа '{character_name}': {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reload")
async def reload_characters_endpoint():
    """Перезагружает всех персонажей."""
    try:
        reload_characters()
        registry = get_character_registry()
        characters = registry.get_character_list()
        
        return JSONResponse(content={
            "message": "Персонажи перезагружены успешно",
            "characters": characters,
            "total": len(characters),
            "status": "success"
        })
    except Exception as e:
        logger.error(f"[ERROR] Ошибка перезагрузки персонажей: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{character_name}/info")
async def get_character_info(character_name: str):
    """Получает краткую информацию о персонаже."""
    try:
        character_data = get_character_data(character_name)
        
        if not character_data:
            raise HTTPException(
                status_code=404, 
                detail=f"Персонаж '{character_name}' не найден"
            )
        
        # Возвращаем только публичную информацию
        public_info = {
            "name": character_data.get("name", character_name),
            "description": character_data.get("description", ""),
            "display_name": character_data.get("display_name", character_name.title()),
            "personality": character_data.get("personality", ""),
            "background": character_data.get("background", ""),
            "traits": character_data.get("traits", []),
            "speaking_style": character_data.get("speaking_style", ""),
        }
        
        return JSONResponse(content={
            "character": public_info,
            "status": "success"
        })
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[ERROR] Ошибка получения информации о персонаже '{character_name}': {e}")
        raise HTTPException(status_code=500, detail=str(e))
