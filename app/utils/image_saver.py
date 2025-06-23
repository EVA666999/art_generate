"""
Модуль для сохранения сгенерированных изображений.
"""
import os
from datetime import datetime
from pathlib import Path
from typing import Union, Optional
import base64
from PIL import Image
import io
from app.config.paths import IMAGES_PATH
import logging
import traceback
from io import BytesIO

logger = logging.getLogger(__name__)

def ensure_images_dir() -> Path:
    """
    Создает директорию для сохранения изображений, если она не существует.
    
    Returns:
        Path: Путь к директории с изображениями
    """
    try:
        logger.info(f"Создаю директорию для изображений: {IMAGES_PATH}")
        IMAGES_PATH.mkdir(parents=True, exist_ok=True)
        logger.info(f"Директория создана/существует: {IMAGES_PATH}")
        logger.info(f"Абсолютный путь: {IMAGES_PATH.absolute()}")
        logger.info(f"Права на запись: {os.access(IMAGES_PATH, os.W_OK)}")
        return IMAGES_PATH
    except Exception as e:
        logger.error(f"Ошибка при создании директории: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise

def save_image(image_data: Union[str, bytes, Image.Image], prefix: str = "image") -> str:
    """
    Сохраняет изображение в директорию images.
    
    Args:
        image_data: Изображение в формате base64 строки, bytes или PIL.Image
        prefix: Префикс для имени файла
        
    Returns:
        str: Путь к сохраненному файлу
    """
    try:
        # Создаем директорию если её нет
        ensure_images_dir()
        
        # Генерируем имя файла
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{prefix}_{timestamp}.png"
        filepath = IMAGES_PATH / filename
        
        logger.info(f"Начинаю сохранение изображения в {filepath}")
        logger.info(f"Абсолютный путь: {filepath.absolute()}")
        
        # Конвертируем входные данные в bytes если нужно
        if isinstance(image_data, str):
            logger.info(f"Получена base64 строка длиной {len(image_data)}")
            try:
                image_bytes = base64.b64decode(image_data)
                logger.info(f"Декодировано {len(image_bytes)} байт из base64")
            except Exception as e:
                logger.error(f"Ошибка декодирования base64: {str(e)}")
                raise
        elif isinstance(image_data, Image.Image):
            logger.info("Получен объект PIL.Image")
            buffer = BytesIO()
            image_data.save(buffer, format="PNG")
            image_bytes = buffer.getvalue()
            logger.info(f"Конвертировано в {len(image_bytes)} байт")
        else:
            logger.info(f"Получены байты длиной {len(image_data)}")
            image_bytes = image_data
            
        # Сохраняем файл
        try:
            with open(filepath, "wb") as f:
                f.write(image_bytes)
            logger.info(f"Файл успешно создан: {filepath}")
            logger.info(f"Размер файла: {os.path.getsize(filepath)} байт")
            
            # Проверяем, что файл действительно создан
            if not os.path.exists(filepath):
                logger.error(f"Файл не был создан: {filepath}")
                raise IOError("Файл не был создан")
                
            return str(filepath)
        except Exception as e:
            logger.error(f"Ошибка при записи файла: {str(e)}")
            raise
            
    except Exception as e:
        logger.error(f"Ошибка при сохранении изображения: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise

def save_base64_image(base64_string: str, prefix: str = "generated") -> str:
    """
    Сохраняет изображение из base64 строки.
    
    Args:
        base64_string: Base64 строка с изображением
        prefix: Префикс для имени файла
        
    Returns:
        str: Путь к сохраненному файлу
    """
    return save_image(base64_string, prefix=prefix) 