"""
Утилиты для сбора и анализа статистики генерации
"""
from typing import Dict, List, Optional
import time
from datetime import datetime, timedelta
import json
import os
import logging
from loguru import logger

class GenerationStats:
    """Класс для сбора и анализа статистики генерации"""
    
    def __init__(self):
        """Инициализация статистики"""
        self.stats_file = "data/generation_stats.json"
        os.makedirs(os.path.dirname(self.stats_file), exist_ok=True)
        
        # Инициализируем базовую структуру статистики
        self.stats = {
            "total_generations": 0,
            "total_time": self._format_time_for_json(0),
            "average_time": self._format_time_for_json(0),
            "by_sampler": {},
            "by_steps": {},
            "by_resolution": {},
            "by_cfg_scale": {},
            "recent_generations": []
        }
        
        logger.info(f"Инициализация GenerationStats. Файл статистики: {self.stats_file}")
        self.stats = self._load_stats()
    
    def _format_time(self, seconds: float) -> str:
        """Форматирует время в читаемый вид"""
        return str(timedelta(seconds=int(seconds)))
        
    def _format_time_for_json(self, seconds: float) -> Dict:
        """Форматирует время для JSON"""
        return {
            "formatted": self._format_time(seconds),
            "total_seconds": seconds
        }
    
    def _load_stats(self) -> Dict:
        """Загружает статистику из файла"""
        try:
            if os.path.exists(self.stats_file):
                with open(self.stats_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Ошибка загрузки статистики: {str(e)}")
        return self.stats
    
    def _save_stats(self) -> None:
        """Сохраняет статистику в файл"""
        try:
            with open(self.stats_file, 'w', encoding='utf-8') as f:
                json.dump(self.stats, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Ошибка сохранения статистики: {str(e)}")
    
    def add_generation(self, params: Dict, execution_time: float, result: Optional[Dict] = None):
        logger.info("Добавление новой генерации в статистику")
        
        # Обновляем общую статистику
        self.stats["total_generations"] += 1
        current_total = self.stats["total_time"]["total_seconds"] + execution_time
        self.stats["total_time"] = self._format_time_for_json(current_total)
        self.stats["average_time"] = self._format_time_for_json(current_total / self.stats["total_generations"])
        
        # Статистика по сэмплеру
        sampler = params["sampler_name"]
        if sampler not in self.stats["by_sampler"]:
            self.stats["by_sampler"][sampler] = {
                "count": 0,
                "total_time": self._format_time_for_json(0),
                "avg_time": self._format_time_for_json(0)
            }
        self.stats["by_sampler"][sampler]["count"] += 1
        current_total = self.stats["by_sampler"][sampler]["total_time"]["total_seconds"] + execution_time
        self.stats["by_sampler"][sampler]["total_time"] = self._format_time_for_json(current_total)
        self.stats["by_sampler"][sampler]["avg_time"] = self._format_time_for_json(
            current_total / self.stats["by_sampler"][sampler]["count"]
        )
        
        # Статистика по шагам
        steps = str(params["steps"])
        if steps not in self.stats["by_steps"]:
            self.stats["by_steps"][steps] = {
                "count": 0,
                "total_time": self._format_time_for_json(0),
                "avg_time": self._format_time_for_json(0)
            }
        self.stats["by_steps"][steps]["count"] += 1
        current_total = self.stats["by_steps"][steps]["total_time"]["total_seconds"] + execution_time
        self.stats["by_steps"][steps]["total_time"] = self._format_time_for_json(current_total)
        self.stats["by_steps"][steps]["avg_time"] = self._format_time_for_json(
            current_total / self.stats["by_steps"][steps]["count"]
        )
        
        # Статистика по разрешению
        resolution = f"{params['width']}x{params['height']}"
        if resolution not in self.stats["by_resolution"]:
            self.stats["by_resolution"][resolution] = {
                "count": 0,
                "total_time": self._format_time_for_json(0),
                "avg_time": self._format_time_for_json(0)
            }
        self.stats["by_resolution"][resolution]["count"] += 1
        current_total = self.stats["by_resolution"][resolution]["total_time"]["total_seconds"] + execution_time
        self.stats["by_resolution"][resolution]["total_time"] = self._format_time_for_json(current_total)
        self.stats["by_resolution"][resolution]["avg_time"] = self._format_time_for_json(
            current_total / self.stats["by_resolution"][resolution]["count"]
        )
        
        # Статистика по CFG Scale
        cfg_scale = str(params["cfg_scale"])
        if cfg_scale not in self.stats["by_cfg_scale"]:
            self.stats["by_cfg_scale"][cfg_scale] = {
                "count": 0,
                "total_time": self._format_time_for_json(0),
                "avg_time": self._format_time_for_json(0)
            }
        self.stats["by_cfg_scale"][cfg_scale]["count"] += 1
        current_total = self.stats["by_cfg_scale"][cfg_scale]["total_time"]["total_seconds"] + execution_time
        self.stats["by_cfg_scale"][cfg_scale]["total_time"] = self._format_time_for_json(current_total)
        self.stats["by_cfg_scale"][cfg_scale]["avg_time"] = self._format_time_for_json(
            current_total / self.stats["by_cfg_scale"][cfg_scale]["count"]
        )
        
        # Добавляем запись о последней генерации
        if "recent_generations" not in self.stats:
            self.stats["recent_generations"] = []
            
        self.stats["recent_generations"].append({
            "timestamp": datetime.utcnow().isoformat(),
            "params": params,
            "execution_time": self._format_time_for_json(execution_time)
        })
        
        # Ограничиваем количество последних генераций до 100
        if len(self.stats["recent_generations"]) > 100:
            self.stats["recent_generations"] = self.stats["recent_generations"][-100:]
        
        # Сохраняем статистику
        self._save_stats()
        logger.info(f"Статистика обновлена. Всего генераций: {self.stats['total_generations']}")
    
    def get_stats_summary(self) -> Dict:
        """Возвращает краткую сводку статистики"""
        return {
            "total_generations": self.stats["total_generations"],
            "total_time": self.stats["total_time"]["formatted"],
            "average_time": self.stats["average_time"]["formatted"],
            "by_sampler": self.stats["by_sampler"],
            "by_steps": self.stats["by_steps"],
            "by_resolution": self.stats["by_resolution"],
            "by_cfg_scale": self.stats["by_cfg_scale"]
        }
    
    def get_recent_generations(self, limit: int = 10) -> List[Dict]:
        """Возвращает последние генерации"""
        return self.stats["recent_generations"][-limit:]
    
    def clear_stats(self) -> None:
        """Очищает статистику"""
        self.stats = {
            "total_generations": 0,
            "total_time": self._format_time_for_json(0),
            "average_time": self._format_time_for_json(0),
            "by_sampler": {},
            "by_steps": {},
            "by_resolution": {},
            "by_cfg_scale": {},
            "recent_generations": []
        }
        self._save_stats()
        logger.info("Статистика очищена")

# Создаем глобальный экземпляр для сбора статистики
generation_stats = GenerationStats() 