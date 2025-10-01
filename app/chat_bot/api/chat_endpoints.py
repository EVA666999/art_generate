#!/usr/bin/env python3
"""
Упрощенные chat endpoints - только один endpoint для чата
"""

import json
import logging
from typing import List, Dict, Optional
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.chat_bot.config.chat_config import chat_config
from app.chat_bot.schemas.chat import SimpleChatRequest, ChatMessage
from app.chat_bot.services.textgen_webui_service import textgen_webui_service
from app.chat_bot.schemas.chat import CharacterConfig
from app.database.db_depends import get_db
from app.chat_bot.models.models import CharacterDB, ChatSession, ChatMessageDB
logger = logging.getLogger(__name__)


def _ensure_character_filled(character_config: CharacterConfig) -> None:
    """Проверяет, что персонаж из БД имеет заполненные Alpaca-поля.
    Если какие-то поля пустые/пробельные, выбрасывает HTTPException 422.
    """
    required = {
        "prompt": character_config.prompt or "",
    }
    missing = [k for k, v in required.items() if not v.strip()]
    if missing:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=422,
            detail=(
                "Персонаж в БД имеет неполные данные. Заполните поля: "
                + ", ".join(missing)
            ),
        )

router = APIRouter(prefix="/api/v1/chat", tags=["Chat"])

# Post-processor удален - не используется


@router.get("/status")
async def get_chat_status():
    """Проверка статуса чата."""
    try:
        is_connected = await textgen_webui_service.check_connection()
        return {
            "status": "ok" if is_connected else "error",
            "textgen_webui_connected": is_connected,
            "message": "Сервис чата работает" if is_connected else "Сервис генерации недоступен"
        }
    except Exception as e:
        logger.error(f"Ошибка проверки статуса: {e}")
        return {
            "status": "error",
            "textgen_webui_connected": False,
            "message": f"Ошибка: {str(e)}"
        }


# Эндпоинт генерации удален - используется только /api/v1/generate-image/ в main.py


@router.post("/stream/name/{character_name}")
async def chat_with_character_stream_by_name(
    character_name: str,
    request: SimpleChatRequest,
    db: AsyncSession = Depends(get_db),
):
    """ЕДИНСТВЕННЫЙ streaming endpoint для чата по имени персонажа.

    Поведение хранения истории:
    - Если request.session_id задан → используем/создаём persistent-сессию (DB),
      загружаем историю и сохраняем новые сообщения.
    - Если request.session_id не задан → работаем статически (ephemeral):
      БД не читаем и не пишем, история берётся только из request.history.
    """
    # Персонаж -> конфиг по имени (поиск без учета регистра)
    result = await db.execute(select(CharacterDB).where(CharacterDB.name.ilike(character_name)))
    db_character = result.scalar_one_or_none()
    if not db_character:
        raise HTTPException(status_code=404, detail="Персонаж не найден")
    
    character_config = CharacterConfig.from_orm(db_character)
    _ensure_character_filled(character_config)
    
    messages: List[ChatMessage] = []
    session: ChatSession | None = None
    character_id = db_character.id

    if request.session_id:
        # По указанному session_id используем существующую persistent-сессию или создаём новую
        result = await db.execute(
            select(ChatSession).where(
                (ChatSession.character_id == character_id)
                & (ChatSession.user_id == request.session_id)
            )
        )
        session = result.scalar_one_or_none()
        if session is None:
            session = ChatSession(character_id=character_id, user_id=request.session_id)
            db.add(session)
            await db.commit()
            await db.refresh(session)

        # Грузим историю только для persistent-сессии
        if session:
            result = await db.execute(
                select(ChatMessageDB)
                .where(ChatMessageDB.session_id == session.id)
                .order_by(ChatMessageDB.timestamp.asc())
                .limit(chat_config.MAX_HISTORY_LENGTH)
            )
            db_messages = result.scalars().all()
            messages = [
                ChatMessage(role=msg.role, content=msg.content)
                for msg in db_messages
            ]
    else:
        # Для ephemeral-режима используем только request.history
        messages = request.history or []

    # Добавляем текущее сообщение пользователя
    messages.append(ChatMessage(role="user", content=request.message))

    # Строим промпт
    message = request.message
    history = messages[:-1]  # Исключаем текущее сообщение из истории для промпта

    # Создаем Alpaca промпт
    character_data = {
        "prompt": character_config.prompt
    }
    alpaca_prompt = textgen_webui_service.build_character_prompt(
        character_data=character_data,
        user_message=message,
        history=history
    )

    # Проверяем подключение к text-generation-webui
    if not await textgen_webui_service.check_connection():
        fallback_response = f"Привет! Я {character_config.name}. К сожалению, сервер генерации текста недоступен."
        
        # Сохраняем fallback-ответ в БД если есть сессия
        if session:
            db.add(ChatMessageDB(session_id=session.id, role="assistant", content=fallback_response))
            await db.commit()
            
        async def generate_stream():
            """Streaming ответ при недоступности LLM сервиса."""
            yield f"data: {json.dumps({'chunk': fallback_response, 'done': True})}\n\n"
            return
        
        return StreamingResponse(
            generate_stream(),
            media_type="text/plain",
            headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
        )

    # Этот блок отвечает за streaming функциональность чат-бота.
    # Изменения здесь могут сломать всю систему streaming чата.
    # 
    # Параметры вызова webui_service.generate_stream() должны точно
    # соответствовать сигнатуре метода в TextGenWebUIService.
    # 
    # КРИТИЧЕСКИЕ ПАРАМЕТРЫ:
    # - НЕ добавлять stream=True (это уже streaming метод)
    # ============================================================================
    
    async def generate_stream():
        """УЛУЧШЕННЫЙ streaming ответ с контекстным пониманием и проверкой завершенности."""
        try:
            # НОВАЯ ЛОГИКА: Проверяем контекст и завершенность предыдущих ответов
            is_continue_story = message.lower().strip() == "continue the story briefly"
            
            # Проверяем, был ли предыдущий ответ завершен
            last_response_complete = True
            if is_continue_story and history:
                last_assistant_msg = None
                for msg in reversed(history):
                    if msg.get('role') == 'assistant':
                        last_assistant_msg = msg.get('content', '')
                        break
                
                if last_assistant_msg:
                    # Проверяем завершенность последнего ответа
                    last_response_complete = _is_response_complete(last_assistant_msg)
                    if not last_response_complete:
                        logger.info(f"📖 Continue the story: Предыдущий ответ не завершен, продолжаем с контекстом")
            
            # Накапливаем весь ответ
            full_response = ""
            
            async for chunk in textgen_webui_service.generate_text_stream(
                prompt=alpaca_prompt,
                max_tokens=request.max_tokens or chat_config.DEFAULT_MAX_TOKENS,
                temperature=request.temperature or chat_config.DEFAULT_TEMPERATURE,
                top_p=request.top_p or chat_config.DEFAULT_TOP_P,
                top_k=request.top_k or chat_config.DEFAULT_TOP_K,
                repeat_penalty=request.repeat_penalty or chat_config.DEFAULT_REPEAT_PENALTY,
                presence_penalty=chat_config.DEFAULT_PRESENCE_PENALTY
            ):
                if chunk:
                    full_response += chunk
            
            # ФИНАЛЬНАЯ ОБРАБОТКА: Убеждаемся, что ответ завершен естественно
            final_response = _ensure_response_completion(full_response, is_continue_story, last_response_complete)
            
            # Отправляем обработанный ответ по частям
            buffer = ""
            for char in final_response:
                buffer += char
                
                # Отправляем буфер, когда накапливается достаточно текста или встречается пробел/знак препинания
                if len(buffer) > 20 or ' ' in buffer or '\n' in buffer or '.' in buffer or ',' in buffer or '!' in buffer or '?' in buffer:
                    # Отправляем накопленный буфер
                    yield f"data: {json.dumps({'chunk': buffer, 'done': False}, ensure_ascii=False)}\n\n"
                    buffer = ""  # Очищаем буфер
            
            # Отправляем оставшийся буфер
            if buffer:
                yield f"data: {json.dumps({'chunk': buffer, 'done': False}, ensure_ascii=False)}\n\n"
            
            # Отправляем сигнал завершения
            yield f"data: {json.dumps({'chunk': '', 'done': True}, ensure_ascii=False)}\n\n"
            
            # Сохраняем полный ответ ассистента в БД
            if session:
                db.add(ChatMessageDB(session_id=session.id, role="assistant", content=final_response))
                await db.commit()
            
            logger.info(f"[OK] Streaming: Ответ сгенерирован с контекстным пониманием")
            
        except Exception as e:
            logger.error(f"[ERROR] Ошибка в streaming генерации: {e}")
            error_data = json.dumps({'error': str(e), 'done': True}, ensure_ascii=False)
            yield f"data: {error_data}\n\n"
    
    def _is_response_complete(response: str) -> bool:
        """
        ИСПРАВЛЕНО: Более строгая проверка завершения ответа.
        
        Args:
            response: Ответ для проверки
            
        Returns:
            True, если ответ завершен
        """
        if not response or not response.strip():
            return False
        
        # Убираем лишние пробелы
        response = response.strip()
        
        # Проверяем, заканчивается ли ответ естественными завершениями
        natural_endings = ['.', '!', '?', '...', '—', '–', '~', '*']
        
        # Проверяем последние символы
        for ending in natural_endings:
            if response.endswith(ending):
                return True
        
        # ИСПРАВЛЕНО: Более строгая проверка незавершенности
        # Если ответ НЕ заканчивается пунктуацией, считаем его незавершенным
        words = response.split()
        if len(words) > 0:
            last_word = words[-1]
            
            # Если последнее слово не заканчивается пунктуацией, это незавершенное предложение
            if not any(last_word.endswith(p) for p in natural_endings):
                # Исключение: если это очень короткое слово (1-2 символа), возможно это артикль или предлог
                if len(last_word) <= 2:
                    return False
                # Исключение: если это слово заканчивается на 's' (множественное число или притяжательный падеж)
                elif last_word.endswith('s') and len(last_word) <= 4:
                    return False
                else:
                    # Все остальные случаи считаем незавершенными
                    return False
        
        return True
    
    def _ensure_response_completion(response: str, is_continue_story: bool, last_response_complete: bool) -> str:
        """
        Обеспечивает естественное завершение ответа.
        
        Args:
            response: Исходный ответ
            is_continue_story: Продолжение истории
            last_response_complete: Был ли предыдущий ответ завершен
            
        Returns:
            Ответ с естественным завершением
        """
        if not response or not response.strip():
            return response
        
        response = response.strip()
        
        # Если ответ уже завершен естественно, возвращаем как есть
        if _is_response_complete(response):
            return response
        
        # Если это продолжение незавершенного ответа, добавляем естественное завершение
        if is_continue_story and not last_response_complete:
            # Добавляем многоточие для продолжения
            if not response.endswith('...'):
                response += "..."
        else:
            # Добавляем точку для завершения
            if not response.endswith(('.', '!', '?')):
                response += "."
        
        return response
    
    # ============================================================================
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
    )


@router.post("/clear_chat")
async def clear_chat(request: SimpleChatRequest):
    """
    Прямой ответ от модели БЕЗ обработчиков, стриминга и пост-процессинга.
    Только чистый ответ от textgen-webui.
    """
    try:
        logger.info(f"🔍 CLEAR CHAT: Получен запрос: {request.message}")
        
        # Получаем персонажа по умолчанию (Anna)
        async with get_db() as db:
            character = await db.execute(
                select(CharacterDB).where(CharacterDB.name == "Anna")
            )
            character = character.scalar_one_or_none()
            
            if not character:
                raise HTTPException(status_code=404, detail="Персонаж Anna не найден")
            
            character_config = CharacterConfig(
                id=character.id,
                name=character.name,
                prompt=character.prompt,
                character_appearance=character.character_appearance,
                location=character.location
            )
        
        # Создаем простой промпт без всех наших обработчиков
        simple_prompt = f"{character_config.prompt}\n\n### Instruction:\n{request.message}\n\n### Response:\n"
        
        logger.info(f"🔍 CLEAR CHAT: Отправляем промпт в textgen-webui: {simple_prompt[:200]}...")
        
        # Прямой вызов textgen-webui БЕЗ обработчиков
        generation_params = {
            "prompt": simple_prompt,
            "max_new_tokens": request.max_tokens or 800,
            "temperature": request.temperature or 0.7,
            "top_p": request.top_p or 0.95,
            "top_k": request.top_k or 50,
            "repeat_penalty": request.repeat_penalty or 1.05,
            "stop": ["</s>"],  # Только базовый стоп-токен
            "stream": False,   # БЕЗ стриминга
            "frequency_penalty": 0.0,
            "presence_penalty": 0.0
        }
        
        # Прямой вызов сервиса
        raw_response = await textgen_webui_service.generate_text(generation_params)
        
        logger.info(f"🔍 CLEAR CHAT: Получен сырой ответ: {raw_response[:200]}...")
        
        return {
            "raw_response": raw_response,
            "prompt_sent": simple_prompt,
            "generation_params": generation_params,
            "character_name": character_config.name,
            "message": "Прямой ответ от модели без обработчиков"
        }
        
    except Exception as e:
        logger.error(f"[ERROR] CLEAR CHAT: Ошибка: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка clear_chat: {str(e)}")


# Обработка ошибок убрана - APIRouter не поддерживает exception_handler