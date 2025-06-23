"""
Утилиты для работы с памятью CUDA и RAM.
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