"""
Универсальный чат API для работы с любыми персонажами.
"""
import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from .character_registry import get_character_data
from app.chat_bot.services.textgen_webui_service import textgen_webui_service
from app.chat_bot.config.chat_config import chat_config

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/chat", tags=["Universal Chat"])


@router.post("/")
async def universal_chat(request: Dict[str, Any]):
    """
    Универсальный эндпоинт для чата с любыми персонажами.
    
    Параметры:
    - message: сообщение пользователя
    - character: имя персонажа (по умолчанию 'anna')
    - history: история сообщений
    - session_id: ID сессии
    """
    try:
        # Извлекаем параметры
        message = request.get("message", "").strip()
        character_name = request.get("character", "anna")
        history = request.get("history", [])
        session_id = request.get("session_id", "default")
        
        # Валидация
        if not message:
            raise HTTPException(status_code=400, detail="Сообщение не может быть пустым")
        
        # Получаем данные персонажа
        character_data = get_character_data(character_name)
        if not character_data:
            raise HTTPException(
                status_code=404, 
                detail=f"Персонаж '{character_name}' не найден"
            )
        
        logger.info(f"[CHAT] Чат с {character_data['name']}: {message[:50]}...")
        
        # Проверяем подключение к text-generation-webui
        if not await textgen_webui_service.check_connection():
            raise HTTPException(
                status_code=503, 
                detail="text-generation-webui недоступен. Запустите сервер text-generation-webui."
            )
        
        # Специальная обработка для "continue the story"
        is_continue_story = message.lower().strip() == "continue the story briefly"
        
        if is_continue_story:
            logger.info(f"[STORY] Continue the story briefly - продолжаем историю кратко")
        else:
            logger.info(f"[GENERATE] Генерируем ответ для: {message[:50]}...")
        
        # Строим простой промпт в формате Alpaca
        if history:
            # Строим историю в формате Alpaca
            history_text = ""
            for msg in history[-10:]:  # Последние 10 сообщений
                if msg.get('role') == 'user':
                    user_content = msg.get('content', '')
                    history_text += f"### Instruction:\n{user_content}\n\n### Response:\n"
                elif msg.get('role') == 'assistant':
                    history_text += f"{msg.get('content', '')}\n\n"
            
            # Строим промпт
            full_prompt = character_data["prompt"] + "\n\n" + history_text
        else:
            # Если истории нет
            if is_continue_story:
                full_prompt = character_data["prompt"] + f"\n\n### Instruction:\ncontinue the story briefly.\n\n### Response:\n"
            else:
                full_prompt = character_data["prompt"] + f"\n\n### Instruction:\n{message}\n\n### Response:\n"
        
        # Генерируем ответ напрямую от модели
        response = await textgen_webui_service.generate_text(
            prompt=full_prompt,
            max_tokens=chat_config.HARD_MAX_TOKENS,
            temperature=chat_config.DEFAULT_TEMPERATURE,
            top_p=chat_config.DEFAULT_TOP_P,
            top_k=chat_config.DEFAULT_TOP_K,
            min_p=chat_config.DEFAULT_MIN_P,
            repeat_penalty=chat_config.DEFAULT_REPEAT_PENALTY,
            presence_penalty=chat_config.DEFAULT_PRESENCE_PENALTY
        )
        
        if not response:
            raise HTTPException(
                status_code=500, 
                detail="Не удалось сгенерировать ответ от модели"
            )
        
        logger.info(f"[OK] Ответ сгенерирован ({len(response)} символов)")
        
        # Возвращаем ответ
        return JSONResponse(content={
            "response": response,
            "character": character_data["name"],
            "character_display_name": character_data.get("display_name", character_data["name"]),
            "session_id": session_id,
            "message": message,
            "is_continue_story": is_continue_story
        })
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[ERROR] Ошибка в универсальном чате: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{character_name}")
async def character_specific_chat(character_name: str, request: Dict[str, Any]):
    """
    Эндпоинт для чата с конкретным персонажем.
    
    Параметры:
    - message: сообщение пользователя
    - history: история сообщений
    - session_id: ID сессии
    """
    # Добавляем имя персонажа в запрос
    request["character"] = character_name
    return await universal_chat(request)
