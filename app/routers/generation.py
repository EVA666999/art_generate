from fastapi import APIRouter, HTTPException, Response, Depends, BackgroundTasks
import base64
import time
import httpx
import json
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime
import os
import traceback
from fastapi.responses import StreamingResponse
from io import BytesIO
from PIL import Image, UnidentifiedImageError

from app.schemas.generation import GenerationRequest, GenerationResponse, GenerationSettings
from app.config.default_prompts import get_default_negative_prompts
from app.config.logging_config import logger
from app.config.settings import settings
import sys
from pathlib import Path

# Добавляем корень проекта в путь для импорта
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app.config.generation_defaults import DEFAULT_GENERATION_PARAMS
from app.utils.lora_utils import lora_manager
from app.utils.controlnet_utils import controlnet_manager
from app.utils.generation_stats import generation_stats
from app.services.face_refinement import FaceRefinementService
from app.core.dependencies import get_face_refinement_service

router = APIRouter(prefix="/api/generation", tags=["generation"])
service = FaceRefinementService(settings.SD_API_URL)

@router.get("/stats")
async def get_generation_stats():
    """Получить статистику генерации изображений"""
    return generation_stats.get_stats_summary()



@router.post("/generate")
async def generate_image(settings: GenerationSettings):
    """Генерация изображения с поддержкой Face Detailer"""
    try:
        logger.info(f"Starting image generation with settings: {settings.dict()}")
        result = await service.generate_image(settings)
        logger.info("Image generation completed successfully")
        
        # Проверяем, что данные не пустые
        if not result.image_data or not result.image_data[0]:
            logger.error("Image data is empty! Возвращаю ошибку 500.")
            raise HTTPException(status_code=500, detail="Image data is empty")

        # Берем первое изображение из списка
        image_data = result.image_data[0]

        # Проверяем, что это валидное изображение
        try:
            img = Image.open(BytesIO(image_data))
            img.verify()
        except Exception as e:
            logger.error(f"Returned data is not a valid image: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Returned data is not a valid image: {str(e)}")

        # Получаем параметры из результата генерации
        info_dict = json.loads(result.info)
        actual_seed = info_dict.get("seed", -1)
        actual_steps = info_dict.get("steps", settings.steps)
        actual_cfg_scale = info_dict.get("cfg_scale", settings.cfg_scale)
        actual_sampler = info_dict.get("sampler_name", settings.sampler_name)
        actual_width = info_dict.get("width", settings.width)
        actual_height = info_dict.get("height", settings.height)

        logger.info(f"Returning image response, size: {len(image_data)} bytes")
        headers = {
            "X-Prompt": settings.prompt,
            "X-Negative-Prompt": settings.get_negative_prompt(),
            "X-Seed": str(actual_seed),
            "X-Steps": str(actual_steps),
            "X-CFG-Scale": str(actual_cfg_scale),
            "X-Sampler": actual_sampler,
            "X-Width": str(actual_width),
            "X-Height": str(actual_height)
        }
        return StreamingResponse(
            BytesIO(image_data),
            media_type="image/png",
            headers=headers
        )
    except Exception as e:
        logger.error(f"Error in generate_image: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))
