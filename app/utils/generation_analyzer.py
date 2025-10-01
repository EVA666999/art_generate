"""
Утилиты для анализа генерации
"""
import os
import json
import re
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from loguru import logger

class GenerationAnalyzer:
    """Класс для анализа генерации"""
    
    def __init__(self, log_dir: str = "logs"):
        """
        :param log_dir: Директория с логами
        """
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        
    def _get_log_files(self, hours: int = 24) -> List[str]:
        """
        Получает список файлов логов за последние hours часов
        
        Args:
            hours: Количество часов для анализа
            
        Returns:
            List[str]: Список путей к файлам логов
        """
        try:
            log_files = []
            current_time = datetime.now()
            
            for file in os.listdir(self.log_dir):
                if not file.endswith(".log"):
                    continue
                    
                file_path = os.path.join(self.log_dir, file)
                file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                
                if current_time - file_time <= timedelta(hours=hours):
                    log_files.append(file_path)
                    
            return sorted(log_files)
        except Exception as e:
            logger.error(f"Error getting log files: {str(e)}")
            return []
            
    def find_multiple_images_issues(self, hours: int = 24) -> List[Dict[str, Any]]:
        """
        Находит проблемы с множественными изображениями
        
        Args:
            hours: Количество часов для анализа
            
        Returns:
            List[Dict[str, Any]]: Список найденных проблем
        """
        try:
            issues = []
            log_files = self._get_log_files(hours)
            
            for log_file in log_files:
                with open(log_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        # Ищем строки с информацией о генерации
                        if "Generated" in line and "images" in line:
                            try:
                                # Извлекаем количество изображений
                                match = re.search(r"Generated (\d+) images", line)
                                if match:
                                    num_images = int(match.group(1))
                                    if num_images > 1:
                                        # Извлекаем timestamp
                                        timestamp_match = re.search(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})", line)
                                        timestamp = timestamp_match.group(1) if timestamp_match else "Unknown"
                                        
                                        # Извлекаем параметры
                                        params_match = re.search(r"Parameters: ({.*})", line)
                                        params = json.loads(params_match.group(1)) if params_match else {}
                                        
                                        issues.append({
                                            "timestamp": timestamp,
                                            "num_images": num_images,
                                            "parameters": params,
                                            "log_file": os.path.basename(log_file)
                                        })
                            except Exception as e:
                                logger.warning(f"Error parsing line: {line}. Error: {str(e)}")
                                continue
                                
            return issues
        except Exception as e:
            logger.error(f"Error finding multiple images issues: {str(e)}")
            return []
            
    def analyze_script_usage(self, hours: int = 24) -> Dict[str, int]:
        """
        Анализирует использование скриптов
        
        Args:
            hours: Количество часов для анализа
            
        Returns:
            Dict[str, int]: Словарь с количеством использований каждого скрипта
        """
        try:
            script_usage = {}
            log_files = self._get_log_files(hours)
            
            for log_file in log_files:
                with open(log_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        # Ищем строки с информацией о скриптах
                        if "Script:" in line:
                            try:
                                # Извлекаем название скрипта
                                match = re.search(r"Script: (.*?)(?:\s|$)", line)
                                if match:
                                    script_name = match.group(1)
                                    script_usage[script_name] = script_usage.get(script_name, 0) + 1
                            except Exception as e:
                                logger.warning(f"Error parsing line: {line}. Error: {str(e)}")
                                continue
                                
            return script_usage
        except Exception as e:
            logger.error(f"Error analyzing script usage: {str(e)}")
            return {}
            
    def get_generation_stats(self, hours: int = 24) -> Dict[str, Any]:
        """
        Получает общую статистику генерации
        
        Args:
            hours: Количество часов для анализа
            
        Returns:
            Dict[str, Any]: Статистика генерации
        """
        try:
            stats = {
                "total_generations": 0,
                "successful_generations": 0,
                "failed_generations": 0,
                "average_time": 0,
                "total_time": 0,
                "by_sampler": {},
                "by_steps": {},
                "by_resolution": {},
                "by_cfg_scale": {}
            }
            
            log_files = self._get_log_files(hours)
            
            for log_file in log_files:
                with open(log_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        # Ищем строки с информацией о генерации
                        if "Generated" in line and "images" in line:
                            try:
                                stats["total_generations"] += 1
                                
                                # Извлекаем параметры
                                params_match = re.search(r"Parameters: ({.*})", line)
                                if params_match:
                                    params = json.loads(params_match.group(1))
                                    
                                    # Обновляем статистику по сэмплеру
                                    sampler = params.get("sampler_name", "unknown")
                                    stats["by_sampler"][sampler] = stats["by_sampler"].get(sampler, 0) + 1
                                    
                                    # Обновляем статистику по шагам
                                    steps = str(params.get("steps", 0))
                                    stats["by_steps"][steps] = stats["by_steps"].get(steps, 0) + 1
                                    
                                    # Обновляем статистику по разрешению
                                    resolution = f"{params.get('width', 0)}x{params.get('height', 0)}"
                                    stats["by_resolution"][resolution] = stats["by_resolution"].get(resolution, 0) + 1
                                    
                                    # Обновляем статистику по CFG Scale
                                    cfg_scale = str(params.get("cfg_scale", 0))
                                    stats["by_cfg_scale"][cfg_scale] = stats["by_cfg_scale"].get(cfg_scale, 0) + 1
                                    
                                # Извлекаем время выполнения
                                time_match = re.search(r"Time: ([\d.]+)s", line)
                                if time_match:
                                    execution_time = float(time_match.group(1))
                                    stats["total_time"] += execution_time
                                    stats["average_time"] = stats["total_time"] / stats["total_generations"]
                                    
                                # Проверяем успешность генерации
                                if "successfully" in line.lower():
                                    stats["successful_generations"] += 1
                                else:
                                    stats["failed_generations"] += 1
                                    
                            except Exception as e:
                                logger.warning(f"Error parsing line: {line}. Error: {str(e)}")
                                continue
                                
            return stats
        except Exception as e:
            logger.error(f"Error getting generation stats: {str(e)}")
            return {} 