"""
Система реестра персонажей для автоматического подключения.
"""
import os
import importlib
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class CharacterRegistry:
    """Реестр персонажей для автоматического подключения."""
    
    def __init__(self):
        """Инициализация реестра персонажей."""
        self.characters: Dict[str, Dict[str, Any]] = {}
        self.characters_dir = Path(__file__).parent.parent / "models" / "characters"
        self._load_characters()
    
    def _load_characters(self) -> None:
        """Загружает всех персонажей из папки characters."""
        try:
            if not self.characters_dir.exists():
                logger.error(f"[ERROR] Папка персонажей не найдена: {self.characters_dir}")
                return
            
            # Сканируем папку на предмет Python файлов
            for file_path in self.characters_dir.glob("*.py"):
                if file_path.name == "__init__.py":
                    continue
                
                character_name = file_path.stem
                try:
                    # Импортируем модуль персонажа
                    module_name = f"app.chat_bot.models.characters.{character_name}"
                    module = importlib.import_module(module_name)
                    
                    # Получаем функцию get_character_data
                    if hasattr(module, 'get_character_data'):
                        character_data = module.get_character_data()
                        
                        # Валидируем данные персонажа
                        if self._validate_character_data(character_data, character_name):
                            self.characters[character_name] = character_data
                            logger.info(f"[OK] Персонаж '{character_name}' загружен успешно")
                        else:
                            logger.warning(f"[WARNING] Персонаж '{character_name}' не прошел валидацию")
                    else:
                        logger.warning(f"[WARNING] В файле {file_path.name} нет функции get_character_data")
                        
                except Exception as e:
                    logger.error(f"[ERROR] Ошибка загрузки персонажа '{character_name}': {e}")
            
            logger.info(f"📚 Загружено персонажей: {len(self.characters)}")
            
        except Exception as e:
            logger.error(f"[ERROR] Ошибка загрузки персонажей: {e}")
    
    def _validate_character_data(self, data: Dict[str, Any], name: str) -> bool:
        """Валидирует данные персонажа с упрощенной структурой."""
        required_fields = ['name', 'character_appearance', 'location']
        
        for field in required_fields:
            if field not in data:
                logger.warning(f"[WARNING] У персонажа '{name}' отсутствует поле '{field}'")
                return False
        
        if not isinstance(data['name'], str) or not data['name'].strip():
            logger.warning(f"[WARNING] У персонажа '{name}' некорректное имя")
            return False
        
        if not isinstance(data['character_appearance'], str) or not data['character_appearance'].strip():
            logger.warning(f"[WARNING] У персонажа '{name}' некорректное описание внешности")
            return False
        
        if not isinstance(data['location'], str) or not data['location'].strip():
            logger.warning(f"[WARNING] У персонажа '{name}' некорректное описание локации")
            return False
        
        return True
    
    def get_character(self, name: str) -> Optional[Dict[str, Any]]:
        """Получает данные персонажа по имени (нечувствительно к регистру)."""
        # Сначала пробуем точное совпадение
        if name in self.characters:
            return self.characters[name]
        
        # Затем пробуем нечувствительный к регистру поиск
        for char_name, char_data in self.characters.items():
            if char_name.lower() == name.lower():
                return char_data
        
        return None
    
    def get_all_characters(self) -> Dict[str, Dict[str, Any]]:
        """Получает всех персонажей."""
        return self.characters.copy()
    
    def get_character_list(self) -> List[Dict[str, str]]:
        """Получает список персонажей для API."""
        return [
            {
                'name': name,
                'description': data.get('description', ''),
                'display_name': data.get('display_name', name.title())
            }
            for name, data in self.characters.items()
        ]
    
    def reload_characters(self) -> None:
        """Перезагружает всех персонажей."""
        logger.info("🔄 Перезагрузка персонажей...")
        self.characters.clear()
        self._load_characters()
    
    def add_character_manually(self, name: str, data: Dict[str, Any]) -> bool:
        """Добавляет персонажа вручную (для тестирования)."""
        if self._validate_character_data(data, name):
            self.characters[name] = data
            logger.info(f"[OK] Персонаж '{name}' добавлен вручную")
            return True
        return False


# Глобальный экземпляр реестра
character_registry = CharacterRegistry()


def get_character_registry() -> CharacterRegistry:
    """Получает глобальный экземпляр реестра персонажей."""
    return character_registry


def get_character_data(character_name: str) -> Optional[Dict[str, Any]]:
    """Получает данные персонажа по имени."""
    return character_registry.get_character(character_name)


def get_all_characters() -> Dict[str, Dict[str, Any]]:
    """Получает всех персонажей."""
    return character_registry.get_all_characters()


def reload_characters() -> None:
    """Перезагружает всех персонажей."""
    character_registry.reload_characters()
