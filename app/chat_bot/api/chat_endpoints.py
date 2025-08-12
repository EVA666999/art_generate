"""
API эндпоинты для чат-бота с кастомными персонажами.
"""
import asyncio
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from io import BytesIO
import json

from app.chat_bot.schemas.chat import (
    ChatMessage, 
    CharacterConfig, 
    MessageRole, 
    SimpleChatRequest
)
from app.chat_bot.models.models import CharacterDB, ChatSession, ChatMessageDB

from app.utils.logger import logger
from app.database.db_depends import get_db
from app.schemas.generation import GenerationSettings
from app.services.face_refinement import FaceRefinementService
from app.chat_bot.config.chat_config import chat_config
from app.chat_bot.services.textgen_webui_service import textgen_webui_service

from app.config.settings import settings

router = APIRouter(prefix="/api/v1/chat", tags=["Chat"])


def _ensure_character_filled(character_config: CharacterConfig) -> None:
    """Проверяет, что персонаж из БД имеет заполненные Alpaca-поля.
    Если какие-то поля пустые/пробельные, выбрасывает HTTPException 422.
    """
    required = {
        "instructions": character_config.instructions or "",
        "system_prompt": character_config.system_prompt or "",
        "response_format": character_config.response_format or "",
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


class ChatWithCharacterRequest(BaseModel):
    messages: List[ChatMessage]
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    top_k: Optional[int] = None
    repeat_penalty: Optional[float] = None


class ImageGenerationRequest(BaseModel):
    prompt: str
    negative_prompt: Optional[str] = None
    use_default_prompts: bool = True
    seed: Optional[int] = None
    steps: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    cfg_scale: Optional[float] = None
    sampler_name: Optional[str] = None


async def get_character_from_db(
    db: AsyncSession, 
    character_id: int
) -> Optional[CharacterDB]:
    """Получает персонажа из БД по ID."""
    result = await db.execute(
        select(CharacterDB).where(CharacterDB.id == character_id)
    )
    return result.scalar_one_or_none()


@router.get("/status")
async def get_chat_status():
    """Получить статус чат-сервиса."""
    # Проверяем подключение к text-generation-webui
    webui_connected = await textgen_webui_service.check_connection()
    
    return {
        "connected": webui_connected,
        "webui_enabled": chat_config.TEXTGEN_WEBUI_ENABLED,
        "webui_url": chat_config.TEXTGEN_WEBUI_URL,
        "model_name": chat_config.TEXTGEN_WEBUI_MODEL,
        "cache_enabled": chat_config.ENABLE_CACHE,
        "max_history_length": chat_config.MAX_HISTORY_LENGTH,
        "max_message_length": chat_config.MAX_MESSAGE_LENGTH,
        "message": "Чат-сервис доступен" if webui_connected else "text-generation-webui недоступен"
    }


@router.post("/webui/chat")
async def chat_with_webui(request: SimpleChatRequest):
    """
    Чат с моделью через text-generation-webui API.
    Использует модель MythoMax L2 13B.
    """
    try:
        # Проверяем подключение к text-generation-webui
        if not await textgen_webui_service.check_connection():
            raise HTTPException(
                status_code=503, 
                detail="text-generation-webui недоступен. Запустите сервер text-generation-webui."
            )
        
        # Строим промпт для MythoMax
        system_message = "Ты полезный ассистент. Отвечай кратко и по делу."
        prompt = textgen_webui_service.build_mythomax_prompt(
            system_message=system_message,
            user_message=request.message,
            history=request.history
        )
        
        logger.info(f"🤖 WebUI: Генерируем ответ для: {request.message[:50]}...")
        
        # Генерируем ответ
        response = await textgen_webui_service.generate_text(
            prompt=prompt,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            top_p=request.top_p,
            top_k=request.top_k,
            repeat_penalty=request.repeat_penalty
        )
        
        if not response:
            raise HTTPException(
                status_code=500, 
                detail="Не удалось сгенерировать ответ от модели"
            )
        
        logger.info(f"✅ WebUI: Ответ сгенерирован ({len(response)} символов)")
        
        return {
            "response": response,
            "model": chat_config.TEXTGEN_WEBUI_MODEL,
            "prompt_length": len(prompt),
            "response_length": len(response),
            "webui_connected": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ WebUI: Ошибка чата: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Внутренняя ошибка сервера: {str(e)}"
        )


@router.post("/webui/chat/stream")
async def chat_with_webui_stream(request: SimpleChatRequest):
    """
    Потоковый чат с моделью через text-generation-webui API.
    Использует модель MythoMax L2 13B.
    """
    try:
        # Проверяем подключение к text-generation-webui
        if not await textgen_webui_service.check_connection():
            raise HTTPException(
                status_code=503, 
                detail="text-generation-webui недоступен. Запустите сервер text-generation-webui."
            )
        
        # Строим промпт для MythoMax
        system_message = "Ты полезный ассистент. Отвечай кратко и по делу."
        prompt = textgen_webui_service.build_mythomax_prompt(
            system_message=system_message,
            user_message=request.message,
            history=request.history
        )
        
        logger.info(f"🤖 WebUI Stream: Генерируем потоковый ответ для: {request.message[:50]}...")
        
        async def generate_stream():
            """Генерирует потоковый ответ."""
            try:
                async for chunk in textgen_webui_service.generate_text_stream(
                    prompt=prompt,
                    max_tokens=request.max_tokens,
                    temperature=request.temperature,
                    top_p=request.top_p,
                    top_k=request.top_k,
                    repeat_penalty=request.repeat_penalty
                ):
                    if chunk:
                        yield f"data: {json.dumps({'chunk': chunk, 'model': chat_config.TEXTGEN_WEBUI_MODEL})}\n\n"
                        
                # Отправляем сигнал завершения
                yield f"data: {json.dumps({'done': True, 'model': chat_config.TEXTGEN_WEBUI_MODEL})}\n\n"
                
            except Exception as e:
                logger.error(f"❌ WebUI Stream: Ошибка потоковой генерации: {e}")
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
        
        return StreamingResponse(
            generate_stream(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Model": chat_config.TEXTGEN_WEBUI_MODEL
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ WebUI Stream: Ошибка чата: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Внутренняя ошибка сервера: {str(e)}"
        )


@router.post("/generate-image")
async def generate_image_in_chat(
    request: ImageGenerationRequest,
    face_refinement_service: FaceRefinementService = Depends(
        lambda: FaceRefinementService(settings.SD_API_URL)
    ),
):
    """
    ИСПРАВЛЕННАЯ: Генерация изображения для чата без дублирования
    """
    try:
        logger.info(
            f"🎯 CHAT: Запрос на генерацию изображения: {request.prompt}"
        )
        
        # Создаем настройки генерации с принудительными параметрами
        generation_settings = GenerationSettings(
            prompt=request.prompt,
            negative_prompt=request.negative_prompt,
            use_default_prompts=request.use_default_prompts,
            seed=request.seed,
            steps=request.steps,
            width=request.width,
            height=request.height,
            cfg_scale=request.cfg_scale,
            sampler_name=request.sampler_name,
            # КРИТИЧЕСКИ ВАЖНО: Принудительно устанавливаем параметры для одного изображения
            batch_size=1,
            n_iter=1,
            save_grid=False,
            # ОТКЛЮЧАЕМ ADetailer
            use_adetailer=False
        )
        
        logger.info("🎯 CHAT: Настройки генерации созданы")
        
        # Генерируем изображение
        result = await face_refinement_service.generate_image(generation_settings)
        
        # НОВОЕ: Проверяем количество полученных изображений
        if not result.image_data or len(result.image_data) == 0:
            raise HTTPException(status_code=500, detail="Не удалось сгенерировать изображение")
        
        if len(result.image_data) > 1:
            logger.warning(f"🔧 CHAT: Получено {len(result.image_data)} изображений, берем только первое")
            # Берем только первое изображение
            image_data = result.image_data[0]
        else:
            # Берем единственное изображение
            image_data = result.image_data[0]
        
        logger.info("✅ CHAT: Изображение успешно сгенерировано")
        
        # Получаем информацию о генерации
        info_dict = {}
        try:
            import json
            info_dict = json.loads(result.info)
        except:
            pass
        
        # Возвращаем изображение как поток
        return StreamingResponse(
            BytesIO(image_data),
            media_type="image/png",
            headers={
                "X-Prompt": request.prompt,
                "X-Seed": str(info_dict.get("seed", result.seed)),
                "X-Steps": str(info_dict.get("steps", request.steps or 40)),
                "X-CFG-Scale": str(info_dict.get("cfg_scale", request.cfg_scale or 6)),
                "X-Sampler": info_dict.get("sampler_name", request.sampler_name or "DPM++ SDE Karras"),
                "X-Width": str(info_dict.get("width", request.width or 768)),
                "X-Height": str(info_dict.get("height", request.height or 768)),
                "X-Images-Generated": "1"  # НОВОЕ: Указываем количество сгенерированных изображений
            }
        )
        
    except Exception as e:
        logger.error(f"❌ CHAT: Ошибка генерации изображения: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка генерации изображения: {str(e)}"
        )

@router.post("/generate-image-base64")
async def generate_image_base64_in_chat(
    request: ImageGenerationRequest,
    face_refinement_service: FaceRefinementService = Depends(lambda: FaceRefinementService(settings.SD_API_URL))
):
    """
    ИСПРАВЛЕННАЯ: Генерация изображения для чата с возвратом в base64 без дублирования
    """
    try:
        logger.info(f"🎯 CHAT: Запрос на генерацию изображения (base64): {request.prompt}")
        
        # Создаем настройки генерации с ПРИНУДИТЕЛЬНЫМ отключением ADetailer
        generation_settings = GenerationSettings(
            prompt=request.prompt,
            negative_prompt=request.negative_prompt,
            use_default_prompts=request.use_default_prompts,
            seed=request.seed,
            steps=request.steps,
            width=request.width,
            height=request.height,
            cfg_scale=request.cfg_scale,
            sampler_name=request.sampler_name,
            # КРИТИЧЕСКИ ВАЖНО: Параметры для ОДНОГО изображения
            batch_size=1,
            n_iter=1,
            save_grid=False,
                                # ОТКЛЮЧАЕМ ADETAILER
                    use_adetailer=False
        )
        
        # Генерируем изображение
        result = await face_refinement_service.generate_image(generation_settings)
        
        # НОВОЕ: Проверяем количество полученных изображений
        if not result.images or len(result.images) == 0:
            raise HTTPException(status_code=500, detail="Не удалось сгенерировать изображение")
        
        if len(result.images) > 1:
            logger.warning(f"🔧 CHAT: Получено {len(result.images)} изображений, берем только первое")
            # Берем только первое изображение
            image_base64 = result.images[0]
        else:
            # Берем единственное изображение
            image_base64 = result.images[0]
        
        logger.info("✅ CHAT: Изображение (base64) успешно сгенерировано")
        
        # Получаем информацию о генерации
        info_dict = {}
        try:
            import json
            info_dict = json.loads(result.info)
        except:
            pass
        
        # Возвращаем JSON с base64 изображением
        return {
            "success": True,
            "image": image_base64,
            "metadata": {
                "prompt": request.prompt,
                "seed": info_dict.get("seed", result.seed),
                "steps": info_dict.get("steps", request.steps or 40),
                "cfg_scale": info_dict.get("cfg_scale", request.cfg_scale or 6),
                "sampler_name": info_dict.get("sampler_name", request.sampler_name or "DPM++ SDE Karras"),
                "width": info_dict.get("width", request.width or 768),
                "height": info_dict.get("height", request.height or 768),
                "images_generated": 1  # НОВОЕ: Указываем количество сгенерированных изображений
            }
        }
        
    except Exception as e:
        logger.error(f"❌ CHAT: Ошибка генерации изображения (base64): {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка генерации изображения: {str(e)}"
        )



@router.post("/{character_id}")
async def chat_with_character(
    character_id: int,
    request: SimpleChatRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Чат с сохраненным в БД персонажем по его ID.
    Поддерживает обычные сообщения и команды !фото/!photo для генерации изображения.
    """
    db_character = await get_character_from_db(db, character_id)
    if db_character is None:
        raise HTTPException(status_code=404, detail="Персонаж не найден")

    character_config = CharacterConfig.from_orm(db_character)
    _ensure_character_filled(character_config)
    if chat_config.LOG_CHAT_REQUESTS:
        logger.info(
            "[CHAR] DB character loaded: name=%s | has_instr=%s | has_sys=%s | has_fmt=%s",
            character_config.name,
            bool(character_config.instructions and character_config.instructions.strip()),
            bool(character_config.system_prompt and character_config.system_prompt.strip()),
            bool(character_config.response_format and character_config.response_format.strip()),
        )
    message = request.message.strip()
    
    # Проверяем команду генерации изображения
    if message.lower().startswith(("!фото", "!photo")):
        prompt = message.split(" ", 1)[1] if " " in message else "photo"
        # Генерация изображения
        generation_settings = GenerationSettings(
            prompt=prompt,
            use_default_prompts=True
        )
        service = FaceRefinementService(settings.SD_API_URL)
        result = await service.generate_image(generation_settings)
        if not result.images or not result.images[0]:
            return {"response": "❌ Не удалось сгенерировать изображение."}
        # LLM сервис отключен
        llm_response = "Фото сгенерировано."
        return {
            "response": llm_response,
            "image": result.images[0]
        }
    
    # Обычная логика чата с персонажем
    messages = []
    
    # Добавляем историю диалога, если есть
    if request.history:
        for msg in request.history:
            if msg.get('role') == 'user':
                messages.append(ChatMessage(
                    role=MessageRole.USER,
                    content=msg['content'],
                    timestamp=None
                ))
            elif msg.get('role') == 'assistant':
                messages.append(ChatMessage(
                    role=MessageRole.ASSISTANT,
                    content=msg['content'],
                    timestamp=None
                ))
    
    # Добавляем текущее сообщение пользователя
    user_message = ChatMessage(
        role=MessageRole.USER,
        content=message,
        timestamp=None
    )
    messages.append(user_message)
    
    # LLM сервис отключен
    return {
        "response": f"Привет! Я {character_config.name}. Сервер генерации текста отключен.",
        "status": "LLM сервис отключен"
    }


@router.post("/character/{character_name}")
async def chat_with_character_by_name(
    character_name: str,
    request: SimpleChatRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Чат с персонажем по имени (из базы данных).
    Поддерживает обычные сообщения и команды !фото/!photo для генерации изображения.
    """
    from sqlalchemy import select
    from app.chat_bot.models.models import CharacterDB
    
    # Получаем персонажа по имени
    result = await db.execute(
        select(CharacterDB).where(CharacterDB.name == character_name)
    )
    db_character = result.scalar_one_or_none()
    
    if db_character is None:
        raise HTTPException(status_code=404, detail="Персонаж не найден")

    character_config = CharacterConfig.from_orm(db_character)
    _ensure_character_filled(character_config)
    if chat_config.LOG_CHAT_REQUESTS:
        logger.info(
            "[CHAR] DB character loaded: name=%s | has_instr=%s | has_sys=%s | has_fmt=%s",
            character_config.name,
            bool(character_config.instructions and character_config.instructions.strip()),
            bool(character_config.system_prompt and character_config.system_prompt.strip()),
            bool(character_config.response_format and character_config.response_format.strip()),
        )
    message = request.message.strip()
    
    # Проверяем команду генерации изображения
    if message.lower().startswith(("!фото", "!photo")):
        prompt = message.split(" ", 1)[1] if " " in message else "photo"
        # Генерация изображения
        generation_settings = GenerationSettings(
            prompt=prompt,
            use_default_prompts=True
        )
        service = FaceRefinementService(settings.SD_API_URL)
        result = await service.generate_image(generation_settings)
        if not result.images or not result.images[0]:
            return {"response": "❌ Не удалось сгенерировать изображение."}
        # LLM сервис отключен
        llm_response = "Фото сгенерировано."
        return {
            "response": llm_response,
            "image": result.images[0]
        }
    
    # Обычная логика чата с персонажем
    messages = []
    
    # Добавляем историю диалога, если есть
    if request.history:
        for msg in request.history:
            if msg.get('role') == 'user':
                messages.append(ChatMessage(
                    role=MessageRole.USER,
                    content=msg['content'],
                    timestamp=None
                ))
            elif msg.get('role') == 'assistant':
                messages.append(ChatMessage(
                    role=MessageRole.ASSISTANT,
                    content=msg['content'],
                    timestamp=None
                ))
    
    # Добавляем текущее сообщение пользователя
    user_message = ChatMessage(
        role=MessageRole.USER,
        content=message,
        timestamp=None
    )
    messages.append(user_message)
    
    # LLM сервис отключен
    return {
        "response": f"Привет! Я {character_config.name}. Сервер генерации текста отключен.",
        "status": "LLM сервис отключен"
    }


@router.post("/file-character/{character_name}")
async def chat_with_file_character(
    character_name: str,
    request: SimpleChatRequest
):
    """
    Чат с персонажем из файла по имени файла.
    Загружает персонажа из app/chat_bot/models/characters/{character_name}.py
    """
    import os
    import importlib.util
    from typing import Dict, Any
    
    try:
        # Путь к файлу персонажа
        characters_dir = "app/chat_bot/models/characters"
        file_path = os.path.join(characters_dir, f"{character_name}.py")
        
        if not os.path.exists(file_path):
            raise HTTPException(
                status_code=404, 
                detail=f"Файл персонажа не найден: {file_path}"
            )
        
        # Загружаем модуль персонажа
        spec = importlib.util.spec_from_file_location(character_name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Получаем данные персонажа
        if not hasattr(module, 'get_character_data'):
            raise HTTPException(
                status_code=500,
                detail=f"Функция get_character_data() не найдена в {character_name}.py"
            )
        
        character_data = module.get_character_data()
        
        # Создаем CharacterConfig из данных файла
        character_config = CharacterConfig(
            name=character_data.get('name', character_name),
            instructions=(
                character_data.get('instructions')
                or "\n".join(
                    [
                        part for part in [
                            character_data.get('behavior'),
                            character_data.get('rules'),
                            character_data.get('speaking_style'),
                            character_data.get('mood')
                        ] if part
                    ]
                )
            ),
            system_prompt=(
                character_data.get('system_prompt')
                or "\n".join(
                    [
                        part for part in [
                            character_data.get('context'),
                            character_data.get('additional_context')
                            if isinstance(character_data.get('additional_context'), str)
                            else None
                        ] if part
                    ]
                )
            ),
            response_format=(
                character_data.get('response_format')
                or f"Answer strictly as {character_data.get('name', character_name)} in first person, without name prefixes."
            )
        )
        
        message = request.message.strip()
        
        # Проверяем команду генерации изображения
        if message.lower().startswith(("!фото", "!photo")):
            prompt = message.split(" ", 1)[1] if " " in message else "photo"
            # Генерация изображения
            generation_settings = GenerationSettings(
                prompt=prompt,
                use_default_prompts=True
            )
            service = FaceRefinementService(settings.SD_API_URL)
            result = await service.generate_image(generation_settings)
            if not result.images or not result.images[0]:
                return {"response": "❌ Не удалось сгенерировать изображение."}
            # LLM сервис отключен
            llm_response = "Фото сгенерировано."
            return {
                "response": llm_response,
                "image": result.images[0]
            }
        
        # Проверяем подключение к text-generation-webui
        if not await textgen_webui_service.check_connection():
            return {
                "response": f"Привет! Я {character_config.name}. К сожалению, сервер генерации текста недоступен. Проверьте, что text-generation-webui запущен.",
                "status": "text-generation-webui недоступен"
            }
        
        # Строим промпт для персонажа
        history = request.history or []
        prompt = textgen_webui_service.build_character_prompt(
            character_data=character_data,
            user_message=message,
            history=history
        )
        
        logger.info(f"🤖 Генерируем ответ для персонажа {character_name}: {message[:50]}...")
        
        # Генерируем ответ через text-generation-webui
        response = await textgen_webui_service.generate_text(
            prompt=prompt,
            max_tokens=chat_config.MYTHOMAX_MAX_TOKENS,
            temperature=chat_config.MYTHOMAX_TEMPERATURE,
            top_p=chat_config.MYTHOMAX_TOP_P,
            top_k=chat_config.MYTHOMAX_TOP_K,
            repeat_penalty=chat_config.MYTHOMAX_REPEAT_PENALTY,
            presence_penalty=chat_config.MYTHOMAX_PRESENCE_PENALTY
        )
        
        if response:
            logger.info(f"✅ Ответ сгенерирован для персонажа {character_name} ({len(response)} символов)")
            return {
                "response": response,
                "character": character_config.name,
                "model": chat_config.TEXTGEN_WEBUI_MODEL,
                "prompt_length": len(prompt),
                "response_length": len(response)
            }
        else:
            return {
                "response": f"Привет! Я {character_config.name}. К сожалению, не удалось сгенерировать ответ. Попробуйте еще раз.",
                "status": "Ошибка генерации"
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка в чате с файловым персонажем {character_name}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка загрузки персонажа: {str(e)}"
        )


@router.post("/stream/file-character/{character_name}")
async def chat_with_file_character_stream(
    character_name: str,
    request: SimpleChatRequest
):
    """
    Streaming чат с файловым персонажем - ответ приходит по мере генерации.
    """
    try:
        # Импортируем персонажа
        if character_name.lower() == "anna":
            from app.chat_bot.models.characters.anna import get_character_data
            character_data = get_character_data()
        else:
            raise HTTPException(
                status_code=404, 
                detail=f"Персонаж {character_name} не найден"
            )
        
        character_config = CharacterConfig(
            name=character_data.get("name", character_name),
            instructions=(
                character_data.get("instructions")
                or "\n".join(
                    [
                        part for part in [
                            character_data.get("behavior"),
                            character_data.get("rules"),
                            character_data.get("speaking_style"),
                            character_data.get("mood"),
                        ] if part
                    ]
                )
            ),
            system_prompt=(
                character_data.get("system_prompt")
                or "\n".join(
                    [
                        part for part in [
                            character_data.get("context"),
                            character_data.get("additional_context")
                            if isinstance(character_data.get("additional_context"), str)
                            else None,
                        ] if part
                    ]
                )
            ),
            response_format=(
                character_data.get("response_format")
                or f"Answer strictly as {character_data.get('name', character_name)} in first person, without name prefixes."
            ),
        )
        
        message = request.message.strip()
        
        # Проверяем подключение к text-generation-webui
        if not await textgen_webui_service.check_connection():
            async def generate_stream():
                """Streaming ответ при недоступности LLM сервиса."""
                try:
                    # Отправляем начальный сигнал
                    yield f"data: {json.dumps({'chunk': '', 'done': False, 'start': True})}\n\n"
                    
                    # Отправляем сообщение о недоступности
                    message = f"Привет! Я {character_config.name}. К сожалению, сервер генерации текста недоступен. Проверьте, что text-generation-webui запущен."
                    chunk_data = {
                        'chunk': message, 
                        'done': False, 
                        'chunk_count': 1
                    }
                    yield f"data: {json.dumps(chunk_data)}\n\n"
                    
                    # Отправляем сигнал завершения
                    final_data = {
                        'chunk': '', 
                        'done': True, 
                        'total_chunks': 1,
                        'success': True
                    }
                    yield f"data: {json.dumps(final_data)}\n\n"
                    
                except Exception as e:
                    logger.error(f"Ошибка streaming чата: {e}")
                    error_data = json.dumps({
                        'error': str(e),
                        'done': True,
                        'success': False
                    })
                    yield f"data: {error_data}\n\n"
            
            return StreamingResponse(
                generate_stream(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive"
                }
            )
        
        # Строим промпт для персонажа
        history = request.history or []
        prompt = textgen_webui_service.build_character_prompt(
            character_data=character_data,
            user_message=message,
            history=history
        )
        
        logger.info(f"🤖 Streaming: Генерируем ответ для персонажа {character_name}: {message[:50]}...")
        
        async def generate_stream():
            """Генерирует потоковый ответ от LLM сервиса."""
            try:
                # Отправляем начальный сигнал
                yield f"data: {json.dumps({'chunk': '', 'done': False, 'start': True})}\n\n"
                
                # Генерируем ответ потоком
                async for chunk in textgen_webui_service.generate_text_stream(
                    prompt=prompt,
                    max_tokens=chat_config.MYTHOMAX_MAX_TOKENS,
                    temperature=chat_config.MYTHOMAX_TEMPERATURE,
                    top_p=chat_config.MYTHOMAX_TOP_P,
                    top_k=chat_config.MYTHOMAX_TOP_K,
                    repeat_penalty=chat_config.MYTHOMAX_REPEAT_PENALTY,
                    presence_penalty=chat_config.MYTHOMAX_PRESENCE_PENALTY
                ):
                    if chunk:
                        chunk_data = {
                            'chunk': chunk, 
                            'done': False, 
                            'chunk_count': 1
                        }
                        yield f"data: {json.dumps(chunk_data)}\n\n"
                
                # Отправляем сигнал завершения
                final_data = {
                    'chunk': '', 
                    'done': True, 
                    'total_chunks': 1,
                    'success': True
                }
                yield f"data: {json.dumps(final_data)}\n\n"
                
            except Exception as e:
                logger.error(f"Ошибка streaming чата: {e}")
                error_data = json.dumps({
                    'error': str(e),
                    'done': True,
                    'success': False
                })
                yield f"data: {error_data}\n\n"
        
        return StreamingResponse(
            generate_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка в streaming чате с файловым персонажем {character_name}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка загрузки персонажа: {str(e)}"
        )


@router.post("/stream_legacy/{character_id}")
async def chat_with_character_stream(
    character_id: int,
    request: SimpleChatRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Streaming чат с персонажем - ответ приходит по мере генерации.
    """
    db_character = await get_character_from_db(db, character_id)
    if db_character is None:
        raise HTTPException(status_code=404, detail="Персонаж не найден")

    character_config = CharacterConfig.from_orm(db_character)
    message = request.message.strip()
    
    # Подготавливаем сообщения
    messages = []
    
    # Добавляем историю диалога, если есть
    if request.history:
        for msg in request.history:
            if msg.get('role') == 'user':
                messages.append(ChatMessage(
                    role=MessageRole.USER,
                    content=msg['content'],
                    timestamp=None
                ))
            elif msg.get('role') == 'assistant':
                messages.append(ChatMessage(
                    role=MessageRole.ASSISTANT,
                    content=msg['content'],
                    timestamp=None
                ))
    
    # Добавляем текущее сообщение пользователя
    user_message = ChatMessage(
        role=MessageRole.USER,
        content=message,
        timestamp=None
    )
    messages.append(user_message)
    
    async def generate_stream():
        """Заглушка для streaming ответа - LLM сервис временно недоступен."""
        try:
            # Отправляем сообщение о недоступности
            message = f"Привет! Я {character_config.name}. К сожалению, интеграция с LLM сервисом временно недоступна."
            yield f"data: {json.dumps({'chunk': message, 'done': False})}\n\n"
            
            # Отправляем сигнал завершения
            yield f"data: {json.dumps({'chunk': '', 'done': True})}\n\n"
            
        except Exception as e:
            logger.error(f"Ошибка streaming чата: {e}")
            yield f"data: {json.dumps({'error': str(e), 'done': True})}\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive"
        }
    ) 


@router.post("/stream/name/{character_name}")
async def chat_with_character_stream_by_name(
    character_name: str,
    request: SimpleChatRequest,
    db: AsyncSession = Depends(get_db),
):
    """Streaming чат по имени персонажа.

    Поведение хранения истории:
    - Если request.session_id задан → используем/создаём persistent-сессию (DB),
      загружаем историю и сохраняем новые сообщения.
    - Если request.session_id не задан → работаем статически (ephemeral):
      БД не читаем и не пишем, история берётся только из request.history.
    """
    # Персонаж -> конфиг по имени
    result = await db.execute(select(CharacterDB).where(CharacterDB.name == character_name))
    db_character = result.scalar_one_or_none()
    if not db_character:
        raise HTTPException(status_code=404, detail="Персонаж не найден")
    
    character_config = CharacterConfig.from_orm(db_character)
    _ensure_character_filled(character_config)
    if chat_config.LOG_CHAT_REQUESTS:
        logger.info(
            f"[CHAR] DB character loaded by name: name={character_config.name} | "
            f"has_instr={bool(character_config.instructions and character_config.instructions.strip())} | "
            f"has_sys={bool(character_config.system_prompt and character_config.system_prompt.strip())} | "
            f"has_fmt={bool(character_config.response_format and character_config.response_format.strip())}"
        )
    
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
        if chat_config.LOG_CHAT_REQUESTS:
            logger.info(
                f"[CHAR] Using persistent session: character_id={character_id}, user_id={request.session_id}"
            )

        # Грузим историю только для persistent-сессии
        result = await db.execute(
            select(ChatMessageDB)
            .where(ChatMessageDB.session_id == session.id)
            .order_by(ChatMessageDB.id.asc())
        )
        history_rows = result.scalars().all()
        for row in history_rows:
            role = MessageRole.USER if row.role == "user" else MessageRole.ASSISTANT
            messages.append(ChatMessage(role=role, content=row.content, timestamp=None))
    else:
        # Нет session_id: всегда создаём новую сессию (пустая история), используем БД
        session = ChatSession(character_id=character_id, user_id=None)
        db.add(session)
        await db.commit()
        await db.refresh(session)
        if chat_config.LOG_CHAT_REQUESTS:
            logger.info(
                f"[CHAR] Created fresh session without user_id for character_id={character_id}"
            )

    # Текущее сообщение пользователя
    user_text = request.message.strip()
    if not user_text:
        raise HTTPException(status_code=400, detail="Пустое сообщение")

    messages.append(ChatMessage(role=MessageRole.USER, content=user_text, timestamp=None))

    # Сохраняем сообщение пользователя
    db.add(ChatMessageDB(session_id=session.id, role="user", content=user_text))
    await db.commit()

    # Подключаемся к text-generation-webui
    try:
        from app.chat_bot.services.textgen_webui_service import TextGenWebUIService
        
        async with TextGenWebUIService() as webui_service:
            # Проверяем соединение
            if not await webui_service.check_connection():
                fallback_response = "Извините, сервер генерации текста недоступен. Проверьте, что text-generation-webui запущен."
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

            # Формируем промпт с использованием build_character_prompt для включения истории
            history = [{"role": msg.role.value, "content": msg.content} for msg in messages[:-1]]
            
            # Преобразуем CharacterConfig в словарь для build_character_prompt
            character_dict = {
                "name": character_config.name,
                "system_prompt": character_config.system_prompt or "",
                "instructions": character_config.instructions,
                "response_format": character_config.response_format or ""
            }
            
            alpaca_prompt = webui_service.build_character_prompt(
                character_dict, 
                user_text, 
                history=history
            )
            
            if chat_config.LOG_CHAT_REQUESTS:
                logger.info(f"🤖 Streaming: Генерируем ответ для персонажа {character_name}: {user_text[:50]}...")
                logger.info(f"📝 Alpaca prompt length: {len(alpaca_prompt)} chars")
                logger.info(f"📚 History messages: {len(history)}")

            # ============================================================================
            # ⚠️  КРИТИЧЕСКИ ВАЖНЫЙ КОД - НЕ ИЗМЕНЯТЬ! ⚠️
            # ============================================================================
            # Этот блок отвечает за streaming функциональность чат-бота.
            # Изменения здесь могут сломать всю систему streaming чата.
            # 
            # Параметры вызова webui_service.generate_stream() должны точно
            # соответствовать сигнатуре метода в TextGenWebUIService.
            # 
            # КРИТИЧЕСКИЕ ПАРАМЕТРЫ:
            # - max_tokens (НЕ max_new_tokens!)
            # - temperature, top_p, top_k, repeat_penalty
            # - НЕ добавлять stream=True (это уже streaming метод)
            # ============================================================================
            
            async def generate_stream():
                try:
                    async for chunk in webui_service.generate_stream(
                        prompt=alpaca_prompt,
                        max_tokens=request.max_tokens or 512,
                        temperature=request.temperature or 0.7,
                        top_p=request.top_p or 0.9,
                        top_k=request.top_k or 40,
                        repeat_penalty=request.repeat_penalty or 1.1
                    ):
                        if chunk and chunk.strip():
                            yield f"data: {json.dumps({'chunk': chunk, 'done': False})}\n\n"
                    
                    # Сигнал завершения
                    yield f"data: {json.dumps({'chunk': '', 'done': True})}\n\n"
                    
                except Exception as e:
                    error_msg = f"Ошибка генерации: {str(e)}"
                    logger.error(f"Ошибка в streaming чате с персонажем {character_name}: {str(e)}")
                    yield f"data: {json.dumps({'error': error_msg, 'done': True})}\n\n"
                finally:
                    # Сохраняем ответ ассистента в БД
                    try:
                        # Получаем полный ответ из стрима (если нужно)
                        pass
                    except Exception as e:
                        logger.error(f"Ошибка сохранения ответа ассистента: {e}")
            
            # ============================================================================
            # ✅ КРИТИЧЕСКИ ВАЖНЫЙ КОД ЗАВЕРШЕН
            # ============================================================================

            return StreamingResponse(
                generate_stream(),
                media_type="text/plain",
                headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
            )

    except Exception as e:
        logger.error(f"Ошибка в streaming чате с персонажем {character_name}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка генерации: {str(e)}")


@router.post("/stream/{character_id}")
async def chat_with_character_stream(
    character_id: int,
    request: SimpleChatRequest,
    db: AsyncSession = Depends(get_db),
):
    """Streaming чат.

    Поведение хранения истории:
    - Если request.session_id задан → используем/создаём persistent-сессию (DB),
      загружаем историю и сохраняем новые сообщения.
    - Если request.session_id не задан → работаем статически (ephemeral):
      БД не читаем и не пишем, история берётся только из request.history.
    """
    # Персонаж -> конфиг
    result = await db.execute(select(CharacterDB).where(CharacterDB.id == character_id))
    db_character = result.scalar_one_or_none()
    if not db_character:
        raise HTTPException(status_code=404, detail="Персонаж не найден")
    character_config = CharacterConfig.from_orm(db_character)
    _ensure_character_filled(character_config)
    if chat_config.LOG_CHAT_REQUESTS:
        logger.info(
            f"[CHAR] DB character loaded: name={character_config.name} | "
            f"has_instr={bool(character_config.instructions and character_config.instructions.strip())} | "
            f"has_sys={bool(character_config.system_prompt and character_config.system_prompt.strip())} | "
            f"has_fmt={bool(character_config.response_format and character_config.response_format.strip())}"
        )
    
    messages: List[ChatMessage] = []
    session: ChatSession | None = None

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
        if chat_config.LOG_CHAT_REQUESTS:
            logger.info(
                f"[CHAR] Using persistent session: character_id={character_id}, user_id={request.session_id}"
            )

        # Грузим историю только для persistent-сессии
        result = await db.execute(
            select(ChatMessageDB)
            .where(ChatMessageDB.session_id == session.id)
            .order_by(ChatMessageDB.id.asc())
        )
        history_rows = result.scalars().all()
        for row in history_rows:
            role = MessageRole.USER if row.role == "user" else MessageRole.ASSISTANT
            messages.append(ChatMessage(role=role, content=row.content, timestamp=None))
    else:
        # Нет session_id: всегда создаём новую сессию (пустая история), используем БД
        session = ChatSession(character_id=character_id, user_id=None)
        db.add(session)
        await db.commit()
        await db.refresh(session)
        if chat_config.LOG_CHAT_REQUESTS:
            logger.info(
                f"[CHAR] Created fresh session without user_id for character_id={character_id}"
            )

    # Текущее сообщение пользователя
    user_text = request.message.strip()
    if not user_text:
        raise HTTPException(status_code=400, detail="Пустое сообщение")

    messages.append(ChatMessage(role=MessageRole.USER, content=user_text, timestamp=None))

    # Сохраняем сообщение пользователя
    db.add(ChatMessageDB(session_id=session.id, role="user", content=user_text))
    await db.commit()

    # Подключаемся к text-generation-webui
    try:
        from app.chat_bot.services.textgen_webui_service import TextGenWebUIService
        
        async with TextGenWebUIService() as webui_service:
            # Проверяем соединение
            if not await webui_service.check_connection():
                fallback_response = "Извините, сервер генерации текста недоступен. Проверьте, что text-generation-webui запущен."
                db.add(ChatMessageDB(session_id=session.id, role="assistant", content=fallback_response))
                await db.commit()
                
                async def generate_stream():
                    """Streaming ответ при недоступности LLM сервиса."""
                    try:
                        message = f"Привет! Я {character_config.name}. К сожалению, сервер генерации текста недоступен."
                        yield f"data: {json.dumps({'chunk': message, 'done': True}, ensure_ascii=False)}\n\n"
                    except Exception as e:
                        logger.error(f"Ошибка streaming чата: {e}")
                        yield f"data: {json.dumps({'error': str(e), 'done': True}, ensure_ascii=False)}\n\n"
                
                return StreamingResponse(
                    generate_stream(),
                    media_type="text/event-stream",
                    headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
                )
            
            # Строим промпт для MythoMax с использованием build_character_prompt
            history = [{"role": msg.role.value, "content": msg.content} for msg in messages[:-1]]
            
            # Преобразуем CharacterConfig в словарь для build_character_prompt
            # Используем только существующие поля из CharacterConfig
            character_dict = {
                "name": character_config.name,
                "system_prompt": character_config.system_prompt or "",
                "instructions": character_config.instructions,
                "response_format": character_config.response_format or ""
            }
            
            prompt = webui_service.build_character_prompt(
                character_dict, 
                user_text, 
                history=history
            )
            
            # ============================================================================
            # ⚠️  КРИТИЧЕСКИ ВАЖНЫЙ КОД - НЕ ИЗМЕНЯТЬ! ⚠️
            # ============================================================================
            # Этот блок отвечает за MythoMax streaming функциональность.
            # Изменения здесь могут сломать всю систему streaming чата.
            # 
            # Параметры вызова webui_service.generate_text_stream() должны точно
            # соответствовать сигнатуре метода в TextGenWebUIService.
            # 
            # КРИТИЧЕСКИЕ ПАРАМЕТРЫ:
            # - max_tokens (использует конфигурацию MYTHOMAX_*)
            # - temperature, top_p, top_k, repeat_penalty, presence_penalty
            # - НЕ добавлять stream=True (это уже streaming метод)
            # ============================================================================
            
            async def generate_stream():
                """Настоящий streaming ответ от LLM сервиса."""
                try:
                    # Используем настоящий стриминг от text-generation-webui
                    full_response = ""
                    async for chunk in webui_service.generate_text_stream(
                         prompt=prompt,
                         max_tokens=chat_config.MYTHOMAX_MAX_TOKENS,
                         temperature=chat_config.MYTHOMAX_TEMPERATURE,
                         top_p=chat_config.MYTHOMAX_TOP_P,
                         top_k=chat_config.MYTHOMAX_TOP_K,
                         repeat_penalty=chat_config.MYTHOMAX_REPEAT_PENALTY,
                         presence_penalty=chat_config.MYTHOMAX_PRESENCE_PENALTY
                     ):
                         if chunk:
                             full_response += chunk
                             # Логируем каждый чанк для отладки
                             logger.info(f"📝 Отправляем чанк: {len(chunk)} символов: {chunk[:50]}...")
                             # Отправляем каждый чанк немедленно
                             yield f"data: {json.dumps({'chunk': chunk, 'done': False}, ensure_ascii=False)}\n\n"
                    
                    # Отправляем сигнал завершения
                    yield f"data: {json.dumps({'chunk': '', 'done': True}, ensure_ascii=False)}\n\n"
                    
                    # Сохраняем полный ответ ассистента в БД
                    if full_response:
                        db.add(ChatMessageDB(session_id=session.id, role="assistant", content=full_response))
                        await db.commit()
                        
                except Exception as e:
                    logger.error(f"Ошибка streaming чата: {e}")
                    yield f"data: {json.dumps({'error': str(e), 'done': True}, ensure_ascii=False)}\n\n"
            
            # ============================================================================
            # ✅ КРИТИЧЕСКИ ВАЖНЫЙ КОД ЗАВЕРШЕН
            # ============================================================================
            
            return StreamingResponse(
                generate_stream(),
                media_type="text/event-stream",
                headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
            )

    except Exception as e:
        logger.error(f"Ошибка подключения к text-generation-webui: {e}")
        fallback_response = f"Извините, произошла ошибка: {str(e)}"
        db.add(ChatMessageDB(session_id=session.id, role="assistant", content=fallback_response))
        await db.commit()
        
        async def generate_stream():
            """Streaming ответ при ошибке подключения."""
            try:
                message = f"Привет! Я {character_config.name}. Произошла ошибка подключения к серверу генерации."
                yield f"data: {json.dumps({'chunk': message, 'done': True}, ensure_ascii=False)}\n\n"
            except Exception as e:
                logger.error(f"Ошибка streaming чата: {e}")
                yield f"data: {json.dumps({'error': str(e), 'done': True}, ensure_ascii=False)}\n\n"
        
        return StreamingResponse(
            generate_stream(),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
        ) 


@router.post("/load-file-character/{character_name}")
async def load_file_character_to_db(
    character_name: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Загружает файлового персонажа в базу данных.
    Позволяет использовать файловых персонажей в основном интерфейсе чата.
    """
    try:
        # Импортируем персонажа
        if character_name.lower() == "anna":
            from app.chat_bot.models.characters.anna import get_character_data
            character_data = get_character_data()
        else:
            raise HTTPException(
                status_code=404, 
                detail=f"Файловый персонаж {character_name} не найден"
            )
        
        # Проверяем, есть ли уже такой персонаж в БД
        existing_character = await db.execute(
            select(CharacterDB).where(CharacterDB.name == character_data["name"])
        )
        existing_character = existing_character.scalar_one_or_none()
        
        if existing_character:
            # Обновляем существующего персонажа
            existing_character.instructions = character_data["instructions"]
            existing_character.system_prompt = character_data["system_prompt"]
            existing_character.response_format = character_data["response_format"]
                            # existing_character.description = character_data.get("description", "")  # Убираем, так как поля description нет
            existing_character.personality = character_data.get("personality", "")
            existing_character.scenario = character_data.get("scenario", "")
            existing_character.first_mes = character_data.get("first_mes", "")
            
            await db.commit()
            await db.refresh(existing_character)
            
            logger.info(f"✅ Персонаж {character_name} обновлен в БД")
            
            return {
                "message": f"Персонаж {character_name} обновлен в базе данных",
                "character": {
                    "id": existing_character.id,
                    "name": existing_character.name,
                    "instructions": existing_character.instructions,
                    "system_prompt": existing_character.system_prompt,
                    "response_format": existing_character.response_format
                }
            }
        else:
            # Создаем нового персонажа
            new_character = CharacterDB(
                name=character_data["name"],
                instructions=character_data["instructions"],
                system_prompt=character_data["system_prompt"],
                response_format=character_data["response_format"],
                description=character_data.get("description", ""),
                personality=character_data.get("personality", ""),
                scenario=character_data.get("scenario", ""),
                first_mes=character_data.get("first_mes", ""),
                is_active=True
            )
            
            db.add(new_character)
            await db.commit()
            await db.refresh(new_character)
            
            logger.info(f"✅ Персонаж {character_name} загружен в БД с ID {new_character.id}")
            
            return {
                "message": f"Персонаж {character_name} загружен в базу данных",
                "character": {
                    "id": new_character.id,
                    "name": new_character.name,
                    "instructions": new_character.instructions,
                    "system_prompt": new_character.system_prompt,
                    "response_format": new_character.response_format
                }
            }
            
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"❌ Ошибка загрузки персонажа {character_name}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка загрузки персонажа: {str(e)}"
        ) 