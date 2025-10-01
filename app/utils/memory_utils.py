"""
Утилиты для управления памятью GPU и исправления ошибок устройств
"""
import gc
import psutil
import torch
import logging
import httpx
from typing import Dict, Any, Optional, Union

logger = logging.getLogger(__name__)


def get_memory_usage() -> Dict[str, Union[float, Dict[str, Union[float, str]]]]:
    """
    Получает информацию об использовании памяти (RAM и GPU).
    
    Returns:
        Dict[str, Union[float, Dict[str, Union[float, str]]]]: Словарь с информацией о памяти
    """
    try:
        process = psutil.Process()
        memory_info: Dict[str, Union[float, Dict[str, Union[float, str]]]] = {
            "rss": process.memory_info().rss / (1024**2),  # MB
            "ram": {
                "total": psutil.virtual_memory().total / (1024**3),  # GB
                "used": psutil.virtual_memory().used / (1024**3),    # GB
                "free": psutil.virtual_memory().free / (1024**3),    # GB
                "percent": psutil.virtual_memory().percent
            }
        }
        
        if torch.cuda.is_available():
            memory_info["gpu"] = {
                "allocated": torch.cuda.memory_allocated() / (1024**3),  # GB
                "cached": torch.cuda.memory_reserved() / (1024**3),      # GB
                "device": torch.cuda.get_device_name(0)
            }
            
        return memory_info
        
    except Exception as e:
        logger.error(f"Ошибка при получении информации о памяти: {str(e)}")
        return {"rss": 0.0, "ram": {}, "gpu": {}}


async def unload_sd_memory(api_url: Optional[str] = None) -> None:
    """
    Очищает память CUDA и выполняет сборку мусора.
    
    Args:
        api_url: URL API Stable Diffusion (опционально)
    """
    try:
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.synchronize()
            
        gc.collect()
        
        # Если передан URL API, пытаемся очистить память через API
        if api_url:
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    await client.post(f"{api_url}/sdapi/v1/unload-checkpoint")
                    logger.info("Memory unloaded via API")
            except Exception as e:
                logger.warning(f"Failed to unload memory via API: {str(e)}")
        
        logger.info("Memory successfully cleaned")
        
    except Exception as e:
        logger.error(f"Error cleaning memory: {str(e)}")


async def clear_gpu_memory(api_url: str) -> bool:
    """
    Очищает память GPU через API WebUI
    
    Args:
        api_url: URL API WebUI
        
    Returns:
        bool: True если очистка прошла успешно
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Очищаем память модели
            response = await client.post(f"{api_url}/sdapi/v1/unload-checkpoint")
            if response.status_code == 200:
                logger.info("Memory unloaded via API")
            else:
                logger.warning(f"Failed to unload memory: {response.status_code}")
            
            # Очищаем кэш CUDA
            response = await client.post(f"{api_url}/sdapi/v1/clear-cache")
            if response.status_code == 200:
                logger.info("CUDA cache cleared")
            else:
                logger.warning(f"Failed to clear cache: {response.status_code}")
                
            return True
            
    except Exception as e:
        logger.error(f"Error clearing GPU memory: {str(e)}")
        return False


async def fix_device_conflict(api_url: str) -> bool:
    """
    Исправляет конфликт устройств (cuda:0 vs cpu)
    
    Args:
        api_url: URL API WebUI
        
    Returns:
        bool: True если исправление прошло успешно
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Перезагружаем модель для исправления конфликта устройств
            response = await client.post(f"{api_url}/sdapi/v1/reload-checkpoint")
            if response.status_code == 200:
                logger.info("Model reloaded to fix device conflict")
                return True
            else:
                logger.warning(f"Failed to reload model: {response.status_code}")
                return False
                
    except Exception as e:
        logger.error(f"Error fixing device conflict: {str(e)}")
        return False


async def get_memory_info(api_url: str) -> Optional[Dict[str, Any]]:
    """
    Получает информацию о памяти GPU
    
    Args:
        api_url: URL API WebUI
        
    Returns:
        Dict[str, Any]: Информация о памяти или None
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{api_url}/sdapi/v1/memory")
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"Failed to get memory info: {response.status_code}")
                return None
                
    except Exception as e:
        logger.error(f"Error getting memory info: {str(e)}")
        return None


async def health_check(api_url: str) -> bool:
    """
    Проверяет здоровье WebUI API
    
    Args:
        api_url: URL API WebUI
        
    Returns:
        bool: True если API работает
    """
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{api_url}/sdapi/v1/progress")
            return response.status_code == 200
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return False 