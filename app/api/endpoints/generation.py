"""
Эндпоинты для генерации изображений
"""
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

from app.schemas.generation import (
    GenerationRequest,
    GenerationResponse,
    GenerationSettings,
    FaceRefinementSettings
)
from app.config.shared_prompts import get_default_negative_prompts
from app.config.logging_config import logger
from app.config.settings import settings
import sys
from pathlib import Path

# Добавляем корень проекта в путь для импорта
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from app.config.shared_config import get_default_generation_params
from app.utils.lora_utils import lora_manager
from app.utils.controlnet_utils import controlnet_manager
from app.utils.generation_stats import generation_stats
from app.services.face_refinement import FaceRefinementService
from app.core.dependencies import get_face_refinement_service

router = APIRouter(tags=["generation"])
service = FaceRefinementService(settings.SD_API_URL)

@router.get("/stats")
async def get_generation_stats():
    """Получить статистику генерации"""
    try:
        return generation_stats.get_stats_summary()
    except Exception as e:
        logger.error(f"Error getting generation stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))



@router.post("/generate")
async def generate_image(settings: GenerationSettings) -> StreamingResponse:
    """
    Генерация изображения с улучшением лиц
    
    Args:
        settings: Настройки генерации
        
    Returns:
        StreamingResponse: Сгенерированное изображение
    """
    try:
        logger.info(f"Received generation request with settings: {settings.dict()}")
        
        # Генерируем изображение
        start_time = time.time()
        result = await service.generate_image(settings)
        execution_time = time.time() - start_time
        
        # Проверяем наличие изображения
        if not result.image_data:
            logger.error("No image data in response")
            raise HTTPException(status_code=500, detail="No image data in response")
            
        # Проверяем валидность изображения
        try:
            image = Image.open(BytesIO(result.image_data))
            image.verify()
        except Exception as e:
            logger.error(f"Invalid image data: {str(e)}")
            raise HTTPException(status_code=500, detail="Invalid image data")
            
        # Возвращаем изображение
        return StreamingResponse(
            BytesIO(result.image_data),
            media_type="image/png"
        )
        
    except Exception as e:
        logger.error(f"Error generating image: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/refine-face", response_model=GenerationResponse)
async def refine_face(
    refinement_settings: FaceRefinementSettings,
    refinement_service: FaceRefinementService = Depends(get_face_refinement_service)
):
    """
    Улучшение лица с помощью ControlNet
    
    Args:
        refinement_settings: Настройки улучшения лица
        refinement_service: Сервис для улучшения лица
        
    Returns:
        GenerationResponse: Результат улучшения лица
    """
    try:
        return await refinement_service.process_face_refinement(refinement_settings)
    except Exception as e:
        logger.error(f"Error refining face: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 