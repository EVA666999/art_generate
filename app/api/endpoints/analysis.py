"""
Endpoints for generation logs analysis
"""
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from app.utils.generation_analyzer import GenerationAnalyzer
from app.config.paths import LOGS_PATH
from loguru import logger

router = APIRouter(tags=["analysis"])

@router.get("/multiple-images")
async def get_multiple_images_issues(hours: int = 24) -> List[Dict[str, Any]]:
    """
    Get list of problems with multiple images
    
    Args:
        hours: Number of hours for analysis
        
    Returns:
        List[Dict[str, Any]]: List of found problems
    """
    try:
        analyzer = GenerationAnalyzer(LOGS_PATH)
        issues = analyzer.find_multiple_images_issues(hours)
        return issues
    except Exception as e:
        logger.error(f"Ошибка при анализе логов: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/script-usage")
async def get_script_usage(hours: int = 24) -> Dict[str, int]:
    """
    Получить статистику использования скриптов
    
    Args:
        hours: Number of hours for analysis
        
    Returns:
        Dict[str, int]: Словарь с количеством использований каждого скрипта
    """
    try:
        analyzer = GenerationAnalyzer(LOGS_PATH)
        script_usage = analyzer.analyze_script_usage(hours)
        return script_usage
    except Exception as e:
        logger.error(f"Ошибка при анализе использования скриптов: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_generation_stats(hours: int = 24) -> Dict[str, Any]:
    """
    Получить общую статистику генерации
    
    Args:
        hours: Number of hours for analysis
        
    Returns:
        Dict[str, Any]: Статистика генерации
    """
    try:
        analyzer = GenerationAnalyzer(LOGS_PATH)
        stats = analyzer.get_generation_stats(hours)
        return stats
    except Exception as e:
        logger.error(f"Ошибка при получении статистики: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 