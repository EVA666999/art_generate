"""
API эндпоинты для чат-бота с кастомными персонажами.
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from io import BytesIO

from chat_bot.schemas.chat import (
    ChatMessage, 
    CharacterConfig, 
    MessageRole, 
    SimpleChatRequest
)
from chat_bot.models.models import CharacterDB
from chat_bot.services.textgen_webui_service import (
    get_textgen_webui_service, 
    TextGenWebUIService
)
from chat_bot.config import chat_config
from utils.logger import logger
from database.db_depends import get_db
from schemas.generation import GenerationSettings
from services.face_refinement import FaceRefinementService
from config.settings import settings

router = APIRouter(prefix="/api/v1/chat", tags=["Chat"])


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
async def get_chat_status(
    textgen_service: TextGenWebUIService = Depends(get_textgen_webui_service)
):
    """Получить статус чат-сервиса (работа через text-generation-webui)."""
    try:
        is_connected = await textgen_service.check_connection()
        model_info = await textgen_service.get_model_info() if is_connected else None
        
        return {
            "connected": is_connected,
            "cache_enabled": chat_config.ENABLE_CACHE,
            "max_history_length": chat_config.MAX_HISTORY_LENGTH,
            "max_message_length": chat_config.MAX_MESSAGE_LENGTH,
            "model_info": model_info
        }
    except Exception as e:
        logger.error(f"Ошибка получения статуса: {e}")
        return {
            "connected": False,
            "error": str(e)
        }

@router.get("/models")
async def get_models(
    textgen_service: TextGenWebUIService = Depends(get_textgen_webui_service)
):
    """Получить список доступных моделей."""
    try:
        models = await textgen_service.get_models()
        return {"models": models}
    except Exception as e:
        logger.error(f"Ошибка получения моделей: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка получения моделей: {str(e)}"
        )

@router.post("/generate-image")
async def generate_image_in_chat(
    request: ImageGenerationRequest,
    face_refinement_service: FaceRefinementService = Depends(lambda: FaceRefinementService(settings.SD_API_URL))
):
    """
    ИСПРАВЛЕННАЯ: Генерация изображения для чата без дублирования
    """
    try:
        logger.info(f"🎯 CHAT: Запрос на генерацию изображения: {request.prompt}")
        
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

@router.post("/models/{model_name}/load")
async def load_model(
    model_name: str,
    textgen_service: TextGenWebUIService = Depends(get_textgen_webui_service)
):
    """Загрузить модель в text-generation-webui."""
    try:
        success = await textgen_service.load_model(model_name)
        if success:
            return {"message": f"Модель {model_name} загружена успешно"}
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Не удалось загрузить модель {model_name}"
            )
    except Exception as e:
        logger.error(f"Ошибка загрузки модели {model_name}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка загрузки модели: {str(e)}"
        )

@router.post("/{character_id}")
async def chat_with_character(
    character_id: int,
    request: SimpleChatRequest,
    db: AsyncSession = Depends(get_db),
    textgen_service: TextGenWebUIService = Depends(get_textgen_webui_service)
):
    """
    Чат с сохраненным в БД персонажем по его ID.
    Поддерживает обычные сообщения и команды !фото/!photo для генерации изображения.
    """
    db_character = await get_character_from_db(db, character_id)
    if db_character is None:
        raise HTTPException(status_code=404, detail="Персонаж не найден")

    character_config = CharacterConfig.from_orm(db_character)
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
        # Генерируем текст-ответ через LLM с персонажем
        llm_prompt = (
            f"Пользователь попросил сгенерировать изображение по запросу: "
            f"'{prompt}'. Ответь как будто ты отправила это фото собеседнику."
        )
        llm_message = ChatMessage(
            role=MessageRole.USER, 
            content=llm_prompt, 
            timestamp=None
        )
        try:
            llm_response, _ = await textgen_service.generate_response(
                messages=[llm_message],
                character_config=character_config
            )
        except Exception as e:
            logger.error(f"Ошибка генерации текста LLM: {e}")
            llm_response = "Фото сгенерировано."
        return {
            "response": llm_response,
            "image": result.images[0]
        }
    
    # Обычная логика чата с персонажем
    user_message = ChatMessage(
        role=MessageRole.USER,
        content=message,
        timestamp=None
    )
    
    try:
        response_text, metadata = await textgen_service.generate_response(
            messages=[user_message],
            character_config=character_config
        )
        return {"response": response_text}
    except Exception as e:
        logger.error(f"Ошибка в чате с персонажем ID {character_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Внутренняя ошибка сервера: {str(e)}"
        )


@router.post("/character/{character_name}")
async def chat_with_character_by_name(
    character_name: str,
    request: SimpleChatRequest,
    db: AsyncSession = Depends(get_db),
    textgen_service: TextGenWebUIService = Depends(get_textgen_webui_service)
):
    """
    Чат с персонажем по имени.
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
        # Генерируем текст-ответ через LLM с персонажем
        llm_prompt = (
            f"Пользователь попросил сгенерировать изображение по запросу: "
            f"'{prompt}'. Ответь как будто ты отправила это фото собеседнику."
        )
        llm_message = ChatMessage(
            role=MessageRole.USER, 
            content=llm_prompt, 
            timestamp=None
        )
        try:
            llm_response, _ = await textgen_service.generate_response(
                messages=[llm_message],
                character_config=character_config
            )
        except Exception as e:
            logger.error(f"Ошибка генерации текста LLM: {e}")
            llm_response = "Фото сгенерировано."
        return {
            "response": llm_response,
            "image": result.images[0]
        }
    
    # Обычная логика чата с персонажем
    user_message = ChatMessage(
        role=MessageRole.USER,
        content=message,
        timestamp=None
    )
    
    try:
        response_text, metadata = await textgen_service.generate_response(
            messages=[user_message],
            character_config=character_config
        )
        return {"response": response_text}
    except Exception as e:
        logger.error(f"Ошибка в чате с персонажем {character_name}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Внутренняя ошибка сервера: {str(e)}"
        ) 