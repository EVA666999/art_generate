"""
API эндпоинты для работы с историей чата.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any
from pydantic import BaseModel

from app.database.db_depends import get_db
from app.auth.dependencies import get_current_user
from app.models.user import Users


router = APIRouter()


class ChatMessageRequest(BaseModel):
    """Запрос для сохранения сообщения."""
    character_name: str
    session_id: str
    message_type: str  # 'user' или 'assistant'
    message_content: str
    image_url: str = None
    image_filename: str = None


class ChatHistoryRequest(BaseModel):
    """Запрос для получения истории чата."""
    character_name: str
    session_id: str


class ClearHistoryRequest(BaseModel):
    """Запрос для очистки истории чата."""
    character_name: str
    session_id: str


@router.post("/save-message")
async def save_chat_message(
    request: ChatMessageRequest,
    current_user: Users = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Сохраняет сообщение в историю чата."""
    try:
        # Импортируем сервис только здесь, чтобы избежать циклических импортов
        from app.chat_history.services.chat_history_service import ChatHistoryService
        history_service = ChatHistoryService(db)
        
        success = await history_service.save_message(
            user_id=current_user.id,
            character_name=request.character_name,
            session_id=request.session_id,
            message_type=request.message_type,
            message_content=request.message_content,
            image_url=request.image_url,
            image_filename=request.image_filename
        )
        
        if success:
            return {"success": True, "message": "Сообщение сохранено в историю"}
        else:
            raise HTTPException(
                status_code=403, 
                detail="У вас нет прав на сохранение истории чата. Требуется подписка Premium или выше."
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка сохранения сообщения: {str(e)}")


@router.post("/get-history")
async def get_chat_history(
    request: ChatHistoryRequest,
    current_user: Users = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Получает историю чата для конкретного персонажа."""
    try:
        # Импортируем сервис только здесь, чтобы избежать циклических импортов
        from app.chat_history.services.chat_history_service import ChatHistoryService
        history_service = ChatHistoryService(db)
        
        history = await history_service.get_chat_history(
            user_id=current_user.id,
            character_name=request.character_name,
            session_id=request.session_id
        )
        
        return {
            "success": True,
            "history": history,
            "can_save_history": await history_service.can_save_history(current_user.id)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения истории: {str(e)}")


@router.get("/characters")
async def get_characters_with_history(
    current_user: Users = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Получает список персонажей с историей чата."""
    try:
        # Импортируем сервис только здесь, чтобы избежать циклических импортов
        from app.chat_history.services.chat_history_service import ChatHistoryService
        history_service = ChatHistoryService(db)
        
        characters = await history_service.get_user_characters_with_history(current_user.id)
        
        return {
            "success": True,
            "characters": characters,
            "can_save_history": await history_service.can_save_history(current_user.id)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения списка персонажей: {str(e)}")


@router.post("/clear-history")
async def clear_chat_history(
    request: ClearHistoryRequest,
    current_user: Users = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Очищает историю чата для конкретного персонажа."""
    try:
        # Импортируем сервис только здесь, чтобы избежать циклических импортов
        from app.chat_history.services.chat_history_service import ChatHistoryService
        history_service = ChatHistoryService(db)
        
        success = await history_service.clear_chat_history(
            user_id=current_user.id,
            character_name=request.character_name,
            session_id=request.session_id
        )
        
        if success:
            return {"success": True, "message": "История чата очищена"}
        else:
            raise HTTPException(
                status_code=403, 
                detail="У вас нет прав на очистку истории чата. Требуется подписка Premium или выше."
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка очистки истории: {str(e)}")


@router.get("/stats")
async def get_history_stats(
    current_user: Users = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Получает статистику по истории чата."""
    try:
        # Импортируем сервис только здесь, чтобы избежать циклических импортов
        from app.chat_history.services.chat_history_service import ChatHistoryService
        history_service = ChatHistoryService(db)
        
        stats = await history_service.get_history_stats(current_user.id)
        
        return {
            "success": True,
            "stats": stats
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения статистики: {str(e)}")
