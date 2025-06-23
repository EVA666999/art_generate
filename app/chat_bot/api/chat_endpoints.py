"""
API эндпоинты для чат-бота с кастомными персонажами.
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.chat_bot.schemas.chat import (
    ChatMessage, 
    CharacterConfig, 
    MessageRole, 
    ChatResponse
)
from app.chat_bot.services.llama_cpp_chat_service import llama_cpp_chat_service
from app.chat_bot.services.character_service import character_service
from app.chat_bot.config import chat_config
from app.utils.logger import logger
from app.database.db_depends import get_db

router = APIRouter(prefix="/api/v1/chat", tags=["Chat"])

class ChatWithCharacterRequest(BaseModel):
    messages: List[ChatMessage]
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    top_k: Optional[int] = None
    repeat_penalty: Optional[float] = None

@router.post("/{character_id}", response_model=ChatResponse)
async def chat_with_character(
    character_id: int, 
    request: ChatWithCharacterRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Чат с сохраненным в БД персонажем по его ID.
    """
    db_character = await character_service.get_character(db, character_id=character_id)
    if db_character is None:
        raise HTTPException(status_code=404, detail="Персонаж не найден")

    character_config = CharacterConfig.from_orm(db_character)
    
    try:
        response_text, metadata = await llama_cpp_chat_service.generate_response(
            messages=request.messages,
            character_config=character_config,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            top_p=request.top_p,
            top_k=request.top_k,
            repeat_penalty=request.repeat_penalty
        )
        
        response = ChatResponse(
            message=response_text,
            character_name=character_config.name,
            tokens_used=metadata.get("tokens_used"),
            generation_time=metadata.get("generation_time"),
            model_info=metadata.get("model_info")
        )
        
        logger.info(f"Успешно сгенерирован ответ для персонажа: {character_config.name} (ID: {character_id})")
        
        return response
        
    except Exception as e:
        logger.error(f"Ошибка в чате с персонажем ID {character_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Внутренняя ошибка сервера: {str(e)}")

@router.get("/status")
async def get_chat_status():
    """Получить статус чат-сервиса."""
    return {
        "model_loaded": llama_cpp_chat_service.is_loaded,
        "model_path": chat_config.MODEL_PATH,
        "cache_enabled": chat_config.ENABLE_CACHE,
        "max_history_length": chat_config.MAX_HISTORY_LENGTH,
        "max_message_length": chat_config.MAX_MESSAGE_LENGTH
    } 