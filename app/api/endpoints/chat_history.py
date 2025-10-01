from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional, List
from app.database.db_depends import get_db
from app.auth.dependencies import get_current_user
from app.models.user import Users
from app.services.chat_history_service import ChatHistoryService


router = APIRouter()


class SaveMessageRequest(BaseModel):
    character_name: str
    message_type: str  # 'user' или 'assistant'
    message_content: str
    session_id: str = "default"  # ID сессии чата
    image_url: Optional[str] = None
    image_filename: Optional[str] = None


class GetHistoryRequest(BaseModel):
    character_name: str


class ChatHistoryResponse(BaseModel):
    id: int
    character_name: str
    message_type: str
    message_content: str
    image_url: Optional[str] = None
    image_filename: Optional[str] = None
    created_at: str


@router.post("/save-message")
async def save_chat_message(
    request: SaveMessageRequest,
    current_user: Users = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Сохраняет сообщение в историю чата."""
    try:
        service = ChatHistoryService(db)
        
        message = await service.save_message(
            user_id=current_user.id,
            character_name=request.character_name,
            message_type=request.message_type,
            message_content=request.message_content,
            session_id=request.session_id,
            image_url=request.image_url,
            image_filename=request.image_filename
        )
        
        return {
            "success": True,
            "message_id": message.id,
            "message": "Сообщение сохранено в историю"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка сохранения сообщения: {str(e)}")


@router.post("/get-history")
async def get_chat_history(
    request: GetHistoryRequest,
    current_user: Users = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Получает историю чата для конкретного персонажа."""
    try:
        service = ChatHistoryService(db)
        
        messages = await service.get_chat_history(
            user_id=current_user.id,
            character_name=request.character_name
        )
        
        history = []
        for msg in messages:
            history.append({
                "id": msg.id,
                "character_name": msg.character_name,
                "message_type": msg.message_type,
                "message_content": msg.message_content,
                "image_url": msg.image_url,
                "image_filename": msg.image_filename,
                "created_at": msg.created_at.isoformat()
            })
        
        return {
            "success": True,
            "character_name": request.character_name,
            "history": history,
            "count": len(history)
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
        service = ChatHistoryService(db)
        
        characters = await service.get_characters_with_history(current_user.id)
        
        return {
            "success": True,
            "characters": characters,
            "count": len(characters)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения персонажей: {str(e)}")


@router.post("/clear-history")
async def clear_chat_history(
    request: GetHistoryRequest,
    current_user: Users = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Очищает историю чата для конкретного персонажа."""
    try:
        service = ChatHistoryService(db)
        
        success = await service.clear_chat_history(
            user_id=current_user.id,
            character_name=request.character_name
        )
        
        return {
            "success": success,
            "message": f"История чата для персонажа '{request.character_name}' {'очищена' if success else 'не найдена'}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка очистки истории: {str(e)}")


@router.get("/stats")
async def get_history_stats(
    current_user: Users = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Получает статистику истории чата пользователя."""
    try:
        service = ChatHistoryService(db)
        
        stats = await service.get_history_stats(current_user.id)
        
        return {
            "success": True,
            "stats": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения статистики: {str(e)}")
