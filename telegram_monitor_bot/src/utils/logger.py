"""
Утилиты для работы с логами
"""
import json
from datetime import datetime
from typing import Dict, List, Any
from pathlib import Path
import aiofiles
from loguru import logger

async def read_generation_stats(file_path: Path) -> List[Dict[str, Any]]:
    """
    Асинхронное чтение статистики генерации из файла
    
    Args:
        file_path: Путь к файлу со статистикой
        
    Returns:
        List[Dict[str, Any]]: Список записей статистики
    """
    try:
        async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
            content = await f.read()
            if not content:
                return []
            return json.loads(content)
    except FileNotFoundError:
        logger.warning(f"Файл {file_path} не найден")
        return []
    except json.JSONDecodeError:
        logger.error(f"Ошибка при чтении JSON из файла {file_path}")
        return []

def format_generation_message(stats: Dict[str, Any]) -> str:
    """
    Форматирование сообщения о генерации
    
    Args:
        stats: Статистика генерации
        
    Returns:
        str: Отформатированное сообщение
    """
    timestamp = datetime.fromisoformat(stats["timestamp"]).strftime("%Y-%m-%d %H:%M:%S")
    settings = stats.get("settings", {})
    
    message = (
        f"🖼 Новая генерация\n"
        f"⏰ Время: {timestamp}\n"
        f"📏 Размер: {settings.get('width', 'N/A')}x{settings.get('height', 'N/A')}\n"
        f"⚙️ Шаги: {settings.get('steps', 'N/A')}\n"
        f"🎯 Sampler: {settings.get('sampler_name', 'N/A')}\n"
        f"⚡️ CFG Scale: {settings.get('cfg_scale', 'N/A')}\n"
        f"⏱ Время выполнения: {stats.get('execution_time', 'N/A'):.2f} сек\n"
    )
    
    if "prompt" in settings:
        message += f"\n📝 Промпт:\n{settings['prompt']}\n"
    
    if "negative_prompt" in settings:
        message += f"\n❌ Негативный промпт:\n{settings['negative_prompt']}\n"
    
    return message 