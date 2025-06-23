from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class StatsManager:
    def __init__(self):
        self.stats = {
            "total_generations": 0,
            "total_time": 0,
            "average_time": 0
        }

    async def add_generation(self, prompt: str, negative_prompt: str, parameters: Dict[str, Any]) -> None:
        """Добавляет информацию о новой генерации в статистику"""
        try:
            self.stats["total_generations"] += 1
            logger.info(f"Добавлена новая генерация в статистику. Всего: {self.stats['total_generations']}")
        except Exception as e:
            logger.error(f"Ошибка при добавлении статистики: {str(e)}")

    def get_stats(self) -> Dict[str, Any]:
        """Возвращает текущую статистику"""
        return self.stats

stats_manager = StatsManager() 