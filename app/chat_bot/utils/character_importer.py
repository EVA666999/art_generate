"""
Утилита для импорта персонажей из файлов в базу данных.
"""
import os
import importlib.util
from typing import Dict, Any, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.chat_bot.models.models import CharacterDB
from app.utils.logger import logger


class CharacterImporter:
    """Импортер персонажей из файлов в базу данных."""
    
    def __init__(self, characters_dir: str = None):
        if characters_dir is None:
            # Автоматически определяем путь к директории персонажей
            current_dir = os.path.dirname(os.path.abspath(__file__))
            self.characters_dir = os.path.join(
                os.path.dirname(os.path.dirname(current_dir)), 
                "chat_bot", "models", "characters"
            )
        else:
            self.characters_dir = characters_dir
    
    def load_character_from_file(self, character_name: str) -> Optional[Dict[str, Any]]:
        """
        Загружает персонажа из файла.
        
        Args:
            character_name: Имя персонажа (без расширения .py)
            
        Returns:
            Словарь с данными персонажа или None
        """
        try:
            file_path = os.path.join(self.characters_dir, f"{character_name}.py")
            
            if not os.path.exists(file_path):
                logger.warning(f"Файл персонажа не найден: {file_path}")
                return None
            
            # Динамически импортируем модуль
            spec = importlib.util.spec_from_file_location(character_name, file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            if not hasattr(module, 'get_character_data'):
                logger.error(f"Функция get_character_data() не найдена в {character_name}.py")
                return None
            
            character_data = module.get_character_data()
            logger.info(f"Персонаж {character_name} успешно загружен из файла")
            return character_data
            
        except Exception as e:
            logger.error(f"Ошибка загрузки персонажа {character_name}: {str(e)}")
            return None
    
    def list_available_characters(self) -> List[str]:
        """Возвращает список доступных персонажей в файлах."""
        try:
            if not os.path.exists(self.characters_dir):
                logger.warning(f"Директория персонажей не найдена: {self.characters_dir}")
                return []
            
            characters = []
            for filename in os.listdir(self.characters_dir):
                if filename.endswith('.py') and not filename.startswith('__'):
                    character_name = filename[:-3]  # Убираем .py
                    characters.append(character_name)
            
            return characters
            
        except Exception as e:
            logger.error(f"Ошибка получения списка персонажей: {str(e)}")
            return []
    
    async def import_character_to_db(
        self, 
        character_name: str, 
        db: AsyncSession,
        overwrite: bool = False
    ) -> Optional[CharacterDB]:
        """
        Импортирует персонажа из файла в базу данных.
        
        Args:
            character_name: Имя персонажа
            db: Сессия базы данных
            overwrite: Перезаписать существующего персонажа
            
        Returns:
            Объект CharacterDB или None
        """
        try:
            # Проверяем, существует ли персонаж в БД (ищем по точному имени и по имени с большой буквы)
            result = await db.execute(
                select(CharacterDB).where(
                    (CharacterDB.name == character_name) | 
                    (CharacterDB.name == character_name.capitalize()) |
                    (CharacterDB.name == character_name.lower())
                )
            )
            existing_char = result.scalar_one_or_none()
            
            if existing_char and not overwrite:
                logger.warning(f"Персонаж {character_name} уже существует в БД. Используйте overwrite=True для перезаписи")
                return existing_char
            
            # Загружаем данные из файла
            character_data = self.load_character_from_file(character_name)
            if not character_data:
                return None
            
            # Создаем или обновляем персонажа в БД
            if existing_char:
                # Обновляем существующего персонажа
                db_char = await self._update_character_in_db(existing_char, character_data, db)
            else:
                # Создаем нового персонажа
                db_char = await self._create_character_in_db(character_data, db)
            
            logger.info(f"Персонаж {character_name} успешно импортирован в БД")
            return db_char
            
        except Exception as e:
            logger.error(f"Ошибка импорта персонажа {character_name}: {str(e)}")
            return None
    
    async def _create_character_in_db(
        self, 
        character_data: Dict[str, Any], 
        db: AsyncSession
    ) -> CharacterDB:
        """Создает нового персонажа в БД с упрощенной структурой."""
        
        # Получаем обязательные поля
        name = character_data.get('name', 'Unknown')
        character_appearance = character_data.get('character_appearance', '')
        location = character_data.get('location', '')
        
        # Создаем базовый промпт из внешности и локации
        prompt = f"Character: {name}"
        if character_appearance:
            prompt += f"\nAppearance: {character_appearance}"
        if location:
            prompt += f"\nLocation: {location}"
        
        db_char = CharacterDB(
            name=name,
            prompt=prompt,
            character_appearance=character_appearance,
            location=location
        )
        
        db.add(db_char)
        await db.commit()
        await db.refresh(db_char)
        return db_char
    
    async def _update_character_in_db(
        self, 
        existing_char: CharacterDB, 
        character_data: Dict[str, Any], 
        db: AsyncSession
    ) -> CharacterDB:
        """Обновляет существующего персонажа в БД с упрощенной структурой."""
        
        # Получаем обязательные поля
        name = character_data.get('name', existing_char.name)
        character_appearance = character_data.get('character_appearance', '')
        location = character_data.get('location', '')
        
        # Создаем базовый промпт из внешности и локации
        prompt = f"Character: {name}"
        if character_appearance:
            prompt += f"\nAppearance: {character_appearance}"
        if location:
            prompt += f"\nLocation: {location}"
        
        # Обновляем поля
        existing_char.name = name
        existing_char.prompt = prompt
        existing_char.character_appearance = character_appearance
        existing_char.location = location
        
        await db.commit()
        await db.refresh(existing_char)
        return existing_char
    

    
    async def import_all_characters(self, db: AsyncSession, overwrite: bool = False) -> List[CharacterDB]:
        """
        Импортирует всех персонажей из файлов в БД.
        
        Args:
            db: Сессия базы данных
            overwrite: Перезаписать существующих персонажей
            
        Returns:
            Список импортированных персонажей
        """
        characters = self.list_available_characters()
        imported = []
        
        for character_name in characters:
            try:
                db_char = await self.import_character_to_db(character_name, db, overwrite)
                if db_char:
                    imported.append(db_char)
            except Exception as e:
                logger.error(f"Ошибка импорта персонажа {character_name}: {str(e)}")
        
        logger.info(f"Импортировано {len(imported)} персонажей из {len(characters)} файлов")
        return imported


# Создаем глобальный экземпляр импортера
character_importer = CharacterImporter() 