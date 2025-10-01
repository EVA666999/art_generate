"""
Утилита для логирования генерации изображений.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import time

class GenerationLogger:
    """Логгер для генерации изображений."""
    
    def __init__(self, logs_dir: str = "generation_logs"):
        """
        Инициализация логгера.
        
        Args:
            logs_dir: Папка для сохранения логов
        """
        self.logs_dir = Path(logs_dir)
        self.logs_dir.mkdir(exist_ok=True)
    
    def log_generation(
        self,
        prompt: str,
        negative_prompt: str,
        character: str,
        settings: Dict[str, Any],
        generation_time: float,
        image_url: str = "",
        success: bool = True,
        error: Optional[str] = None,
        enhanced_prompt: Optional[str] = None,
        enhanced_negative_prompt: Optional[str] = None
    ) -> None:
        """
        Логирует информацию о генерации изображения.
        
        Args:
            prompt: Базовый промпт пользователя
            negative_prompt: Базовый негативный промпт пользователя
            character: Имя персонажа
            settings: Настройки генерации
            generation_time: Время генерации в секундах
            image_url: URL сгенерированного изображения (без base64)
            success: Успешность генерации
            error: Сообщение об ошибке (если есть)
            enhanced_prompt: Улучшенный промпт с дефолтными промптами
            enhanced_negative_prompt: Улучшенный негативный промпт
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "success": success,
            "generation_time_seconds": round(generation_time, 2),
            "character": character,
            
            # Промпты - детальная информация
            "prompts": {
                "user_prompt": prompt,
                "user_negative_prompt": negative_prompt,
                "enhanced_prompt": enhanced_prompt or prompt,
                "enhanced_negative_prompt": enhanced_negative_prompt or negative_prompt,
                "prompt_length": len(enhanced_prompt or prompt),
                "negative_prompt_length": len(enhanced_negative_prompt or negative_prompt),
                "uses_default_prompts": settings.get("use_default_prompts", True)
            },
            
            # URL изображения (без base64)
            "image_url": image_url if not image_url.startswith("data:image") else "base64_image_omitted",
            "settings": {
                # Основные параметры генерации
                "width": settings.get("width"),
                "height": settings.get("height"),
                "steps": settings.get("steps"),
                "cfg_scale": settings.get("cfg_scale"),
                "sampler_name": settings.get("sampler_name"),
                "scheduler": settings.get("scheduler"),
                "seed": settings.get("seed"),
                "batch_size": settings.get("batch_size"),
                "n_iter": settings.get("n_iter"),
                "n_samples": settings.get("n_samples"),
                "save_grid": settings.get("save_grid"),
                "restore_faces": settings.get("restore_faces"),
                "send_images": settings.get("send_images"),
                "save_images": settings.get("save_images"),
                
                # High-res fix параметры
                "enable_hr": settings.get("enable_hr", False),
                "hr_scale": settings.get("hr_scale"),
                "hr_upscaler": settings.get("hr_upscaler"),
                "hr_second_pass_steps": settings.get("hr_second_pass_steps"),
                "hr_prompt": settings.get("hr_prompt"),
                "hr_negative_prompt": settings.get("hr_negative_prompt"),
                "denoising_strength": settings.get("denoising_strength"),
                
                # Дополнительные параметры
                "clip_skip": settings.get("clip_skip"),
                "use_default_prompts": settings.get("use_default_prompts", True),
                "override_settings": settings.get("override_settings", {}),
                "override_settings_restore_afterwards": settings.get("override_settings_restore_afterwards", False),
                "script_args": settings.get("script_args", []),
                
                # ADetailer настройки
                "use_adetailer": settings.get("use_adetailer", False),
                "adetailer_settings": settings.get("adetailer_settings", {}),
                
                # IP-Adapter настройки
                "ip_adapter_model": settings.get("ip_adapter_model"),
                "ip_adapter_weight": settings.get("ip_adapter_weight"),
                "ip_adapter_image": settings.get("ip_adapter_image"),
                
                # LoRA модели - детальная информация с проверкой работы
                "lora_models": self._check_lora_models(settings.get("lora_models", [])),
                
                # Alwayson scripts - детальная информация
                "alwayson_scripts": {
                    "adetailer_enabled": "ADetailer" in settings.get("alwayson_scripts", {}),
                    "adetailer_config": settings.get("alwayson_scripts", {}).get("ADetailer", {}),
                    "controlnet_enabled": "ControlNet" in settings.get("alwayson_scripts", {}),
                    "all_scripts": list(settings.get("alwayson_scripts", {}).keys())
                }
            },
            "error": error
        }
        
        # Сохраняем в файл с датой
        date_str = datetime.now().strftime("%Y%m%d")
        log_file = self.logs_dir / f"generation_{date_str}.jsonl"
        
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False, indent=2) + "\n\n")
    
    def get_stats(self, days: int = 7) -> Dict[str, Any]:
        """
        Получает статистику генерации за последние дни.
        
        Args:
            days: Количество дней для анализа
            
        Returns:
            Словарь со статистикой
        """
        stats = {
            "total_generations": 0,
            "successful_generations": 0,
            "failed_generations": 0,
            "average_generation_time": 0,
            "characters_used": {},
            "total_generation_time": 0
        }
        
        total_time = 0
        successful_count = 0
        
        for i in range(days):
            date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            date = date.replace(day=date.day - i)
            date_str = date.strftime("%Y%m%d")
            log_file = self.logs_dir / f"generation_{date_str}.jsonl"
            
            if not log_file.exists():
                continue
                
            with open(log_file, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        try:
                            entry = json.loads(line)
                            stats["total_generations"] += 1
                            
                            if entry["success"]:
                                stats["successful_generations"] += 1
                                successful_count += 1
                                total_time += entry["generation_time_seconds"]
                            else:
                                stats["failed_generations"] += 1
                            
                            # Статистика по персонажам
                            character = entry.get("character", "unknown")
                            stats["characters_used"][character] = stats["characters_used"].get(character, 0) + 1
                            
                        except json.JSONDecodeError:
                            continue
        
        if successful_count > 0:
            stats["average_generation_time"] = round(total_time / successful_count, 2)
        
        stats["total_generation_time"] = round(total_time, 2)
        
        return stats
    
    def _check_lora_models(self, lora_models: list) -> Dict[str, Any]:
        """
        Проверяет работу LoRA моделей и возвращает детальную информацию.
        
        Args:
            lora_models: Список LoRA моделей из настроек
            
        Returns:
            Словарь с информацией о LoRA моделях
        """
        lora_status = {
            "enabled_loras": [],
            "disabled_loras": [],
            "total_loras": len(lora_models),
            "working_loras": [],
            "not_working_loras": [],
            "lora_details": []
        }
        
        for lora in lora_models:
            lora_name = lora.get("name", "unknown")
            lora_weight = lora.get("weight", 0)
            lora_enabled = lora.get("enabled", False)
            
            # Проверяем, работает ли LoRA модель
            is_working = self._is_lora_working(lora_name, lora_weight, lora_enabled)
            
            lora_info = {
                "name": lora_name,
                "weight": lora_weight,
                "enabled": lora_enabled,
                "working": is_working,
                "status": "работает" if is_working else "не работает"
            }
            
            lora_status["lora_details"].append(lora_info)
            
            if lora_enabled:
                lora_status["enabled_loras"].append(lora_name)
                if is_working:
                    lora_status["working_loras"].append(lora_name)
                else:
                    lora_status["not_working_loras"].append(lora_name)
            else:
                lora_status["disabled_loras"].append(lora_name)
        
        return lora_status
    
    def _is_lora_working(self, lora_name: str, lora_weight: float, lora_enabled: bool) -> bool:
        """
        Проверяет, работает ли LoRA модель.
        
        Args:
            lora_name: Название LoRA модели
            lora_weight: Вес LoRA модели
            lora_enabled: Включена ли LoRA модель
            
        Returns:
            True если LoRA работает, False если нет
        """
        if not lora_enabled:
            return False
            
        if lora_weight <= 0:
            return False
            
        # Проверяем, существует ли файл LoRA модели
        lora_paths = [
            f"stable-diffusion-webui/models/Lora/{lora_name}",
            f"stable-diffusion-webui/models/Lora/{lora_name}.safetensors",
            f"stable-diffusion-webui/models/Lora/{lora_name}.pt",
            f"stable-diffusion-webui/models/Lora/{lora_name}.ckpt"
        ]
        
        for path in lora_paths:
            if os.path.exists(path):
                return True
                
        return False
