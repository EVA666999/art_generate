import json
import os
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

class LoraManager:
    def __init__(self):
        self.lora_config: Dict[str, Any] = {
            "enabled": False,
            "models": {},
            "default_settings": {
                "model_type": "SD 1.5"
            }
        }
        self.load_config()

    def load_config(self) -> None:
        """Загружает конфигурацию LORA из файла"""
        try:
            config_path = os.path.join("app", "config", "lora_config.json")
            if os.path.exists(config_path):
                with open(config_path, "r", encoding="utf-8") as f:
                    loaded_config = json.load(f)
                    self.lora_config.update(loaded_config)
                logger.info("LORA конфигурация загружена")
            else:
                logger.warning("Файл конфигурации LORA не найден")
        except Exception as e:
            logger.error(f"Ошибка при загрузке конфигурации LORA: {str(e)}")

    def get_all_lora_prompts(self) -> str:
        """Возвращает все активные LORA промпты"""
        if not self.lora_config.get("enabled", False):
            return ""
            
        prompts = []
        for model_name, config in self.lora_config.get("models", {}).items():
            if config.get("enabled", False):
                weight = config.get("weight", 1.0)
                prompts.append(f"<lora:{model_name}:{weight}>")
        return " ".join(prompts)

    def get_lora_prompt(self, lora_name: str, weight: Optional[float] = None) -> str:
        """
        Получает промпт для LORA модели
        
        Args:
            lora_name: Имя LORA модели
            weight: Вес LORA (если None, используется вес из конфига)
            
        Returns:
            str: Промпт с LORA
        """
        if not self.lora_config.get("enabled", False):
            return ""
            
        model_config = self.lora_config.get("models", {}).get(lora_name)
        if not model_config:
            return ""
            
        if weight is None:
            weight = model_config.get("weight", 1.0)
            
        prompt_template = model_config.get("prompt_template", "")
        return prompt_template.replace(str(model_config.get("weight", 1.0)), str(weight))
    
    def get_recommended_weight(self, lora_name: str, feature_type: str) -> float:
        """
        Получает рекомендуемый вес для LORA модели
        
        Args:
            lora_name: Имя LORA модели
            feature_type: Тип фичи (face, ass и т.д.)
            
        Returns:
            float: Рекомендуемый вес
        """
        model_config = self.lora_config.get("models", {}).get(lora_name)
        if not model_config or "recommended_weights" not in model_config:
            return model_config.get("weight", 1.0) if model_config else 1.0
            
        feature_weights = model_config.get("recommended_weights", {}).get(feature_type)
        if not feature_weights:
            return model_config.get("weight", 1.0)
            
        return feature_weights.get("default", 1.0)
    
    def get_model_type(self, lora_name: str) -> str:
        """
        Получает тип модели для LORA
        
        Args:
            lora_name: Имя LORA модели
            
        Returns:
            str: Тип модели (SD 1.5 или SDXL)
        """
        model_config = self.lora_config.get("models", {}).get(lora_name)
        if not model_config:
            return self.lora_config.get("default_settings", {}).get("model_type", "SD 1.5")
            
        return model_config.get("model_type", self.lora_config.get("default_settings", {}).get("model_type", "SD 1.5"))

# Создаем глобальный экземпляр для использования в приложении
lora_manager = LoraManager() 