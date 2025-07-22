"""
Сервис для работы с персонажами через ООП.
"""
from typing import List, Dict, Any, Optional
from app.chat_bot.models.character import Character, CharacterTraits
from app.chat_bot.schemas.chat import ChatMessage, MessageRole
from app.utils.logger import logger
from sqlalchemy import select
from app.chat_bot.models.models import CharacterDB
import os
import importlib
import json


class CharacterService:
    """Сервис для управления персонажами и чатом."""
    
    def __init__(self):
        self.characters = {}
        self._load_characters()
    
    def _load_characters(self):
        """Загружает всех персонажей из папки characters."""
        characters_dir = os.path.join(os.path.dirname(__file__), '../models/characters')
        abs_dir = os.path.abspath(characters_dir)
        for filename in os.listdir(abs_dir):
            if filename.endswith('.py') and filename != '__init__.py':
                char_name = filename[:-3]
                try:
                    module = importlib.import_module(f"app.chat_bot.models.characters.{char_name}")
                    char_data = module.get_character_data()
                    traits = CharacterTraits(
                        personality=char_data["personality"],
                        background=char_data["background"],
                        speaking_style=char_data["speaking_style"],
                        interests=char_data["interests"],
                        mood=char_data["mood"],
                        additional_context=char_data.get("additional_context"),
                        age=char_data.get("age"),
                        profession=char_data.get("profession"),
                        behavior=char_data.get("behavior"),
                        appearance=char_data.get("appearance"),
                        voice=char_data.get("voice"),
                        rules=char_data.get("rules"),
                        context=char_data.get("context")
                    )
                    character = Character(char_data["name"], traits)
                    self.characters[char_data["name"]] = character
                except Exception as e:
                    print(f"Ошибка загрузки персонажа {char_name}: {e}")
    
    def create_character(self, name: str) -> Character:
        """Создает персонажа по имени."""
        try:
            character = Character.create(name)
            self.characters[name] = character
            logger.info(f"Создан персонаж: {name}")
            return character
        except Exception as e:
            logger.error(f"Ошибка создания персонажа: {str(e)}")
            raise
    
    def get_character(self, name: str) -> Optional[Character]:
        """Получает персонажа по имени."""
        return self.characters.get(name)
    
    def list_characters(self) -> List[Dict[str, Any]]:
        """Возвращает список всех персонажей."""
        return [
            {
                "name": char.name,
                "personality": char.traits.personality,
                "mood": char.traits.mood,
                "interests": char.traits.interests
            }
            for char in self.characters.values()
        ]
    
    async def chat_with_character(
        self,
        character_name: str,
        message: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None
    ) -> Dict[str, Any]:
        """Ведет диалог с персонажем."""
        try:
            character = self.get_character(character_name)
            if not character:
                raise ValueError(f"Персонаж не найден: {character_name}")
            
            # Добавляем сообщение пользователя в историю
            character.add_message("user", message)
            
            # Конвертируем историю в формат для API
            history = character.get_conversation_history()
            messages = [
                ChatMessage(
                    role=MessageRole.USER if msg["role"] == "user" else MessageRole.ASSISTANT,
                    content=msg["content"],
                    timestamp=msg["timestamp"]
                )
                for msg in history
            ]
            
            # Конвертируем character в CharacterConfig
            from app.chat_bot.schemas.chat import CharacterConfig
            character_config = CharacterConfig(
                name=character.name,
                personality=character.traits.personality,
                background=character.traits.background,
                speaking_style=character.traits.speaking_style,
                interests=character.traits.interests,
                mood=character.traits.mood,
                additional_context=character.traits.additional_context,
                age=character.traits.age,
                profession=character.traits.profession,
                behavior=character.traits.behavior,
                appearance=character.traits.appearance,
                voice=character.traits.voice,
                rules=character.traits.rules,
                context=character.traits.context
            )
            
            # Генерируем ответ (пока заглушка)
            response = f"Ответ от {character.name}: {message}"
            metadata = {"method": "placeholder"}
            
            # Добавляем ответ персонажа в историю
            character.add_message("assistant", response)
            
            return {
                "character_name": character.name,
                "response": response,
                "metadata": metadata,
                "conversation_length": len(character.conversation_history)
            }
            
        except Exception as e:
            logger.error(f"Ошибка в чате с персонажем {character_name}: {str(e)}")
            raise
    
    def get_character_prompt(self, character_name: str) -> str:
        """Получает system prompt персонажа."""
        character = self.get_character(character_name)
        if not character:
            raise ValueError(f"Персонаж не найден: {character_name}")
        return character.get_system_prompt()
    
    def update_character_mood(self, character_name: str, new_mood: str) -> bool:
        """Обновляет настроение персонажа."""
        character = self.get_character(character_name)
        if not character:
            return False
        
        character.traits.mood = new_mood
        logger.info(f"Настроение персонажа {character_name} изменено на: {new_mood}")
        return True
    
    def get_characters_by_type(self, character_type: str) -> List[Dict[str, Any]]:
        """Возвращает персонажей определенного типа."""
        # Пока возвращаем всех персонажей, так как у нас нет типов
        return self.list_characters()
    
    def clear_character_history(self, character_name: str) -> bool:
        """Очищает историю диалога персонажа."""
        character = self.get_character(character_name)
        if not character:
            return False
        
        character.conversation_history.clear()
        logger.info(f"История персонажа {character_name} очищена")
        return True

    async def get_characters(self, db, skip: int = 0, limit: int = 100):
        """
        Возвращает список персонажей из базы данных.
        """
        result = await db.execute(
            select(CharacterDB).offset(skip).limit(limit)
        )
        return result.scalars().all()

    async def add_to_db(self, character, db):
        from app.chat_bot.models.models import CharacterDB
        
        db_char = CharacterDB(
            name=character.name,
            personality=character.traits.personality,
            background=character.traits.background,
            speaking_style=character.traits.speaking_style,
            interests=character.traits.interests,
            mood=character.traits.mood,
            additional_context=character.traits.additional_context,
            age=character.traits.age,
            profession=character.traits.profession,
            behavior=character.traits.behavior,
            appearance=character.traits.appearance,
            voice=character.traits.voice,
            rules=character.traits.rules,
            context=character.traits.context
        )
        db.add(db_char)
        await db.commit()
        await db.refresh(db_char)
        return db_char

    async def update_in_db(self, character, db):
        from app.chat_bot.models.models import CharacterDB
        from sqlalchemy import select
        result = await db.execute(select(CharacterDB).where(CharacterDB.name == character.name))
        db_char = result.scalar_one_or_none()
        if not db_char:
            return None
        
        db_char.personality = character.traits.personality
        db_char.background = character.traits.background
        db_char.speaking_style = character.traits.speaking_style
        db_char.interests = character.traits.interests
        db_char.mood = character.traits.mood
        db_char.additional_context = character.traits.additional_context
        db_char.age = character.traits.age
        db_char.profession = character.traits.profession
        db_char.behavior = character.traits.behavior
        db_char.appearance = character.traits.appearance
        db_char.voice = character.traits.voice
        db_char.rules = character.traits.rules
        db_char.context = character.traits.context
        await db.commit()
        await db.refresh(db_char)
        return db_char

    async def delete_from_db(self, character_name, db):
        from app.chat_bot.models.models import CharacterDB
        result = await db.execute(
            select(CharacterDB).where(CharacterDB.name == character_name)
        )
        db_char = result.scalar_one_or_none()
        if not db_char:
            return None
        await db.delete(db_char)
        await db.commit()
        return db_char


# Создаем глобальный экземпляр сервиса
character_service = CharacterService() 