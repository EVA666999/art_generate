from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.chat_bot.models.character import Character
from app.chat_bot.schemas.chat import CharacterCreate, CharacterUpdate

class CharacterService:
    async def get_character(self, db: AsyncSession, character_id: int) -> Optional[Character]:
        """Получает персонажа по ID."""
        result = await db.execute(select(Character).filter(Character.id == character_id))
        return result.scalars().first()

    async def get_characters(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Character]:
        """Получает список персонажей."""
        result = await db.execute(select(Character).offset(skip).limit(limit))
        return result.scalars().all()

    async def create_character(self, db: AsyncSession, character: CharacterCreate) -> Character:
        """Создает нового персонажа."""
        db_character = Character(**character.dict())
        db.add(db_character)
        await db.commit()
        await db.refresh(db_character)
        return db_character

    async def update_character(
        self, db: AsyncSession, character_id: int, character_update: CharacterUpdate
    ) -> Optional[Character]:
        """Обновляет существующего персонажа."""
        db_character = await self.get_character(db, character_id)
        if db_character:
            update_data = character_update.dict(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_character, key, value)
            await db.commit()
            await db.refresh(db_character)
        return db_character

    async def delete_character(self, db: AsyncSession, character_id: int) -> Optional[Character]:
        """Удаляет персонажа."""
        db_character = await self.get_character(db, character_id)
        if db_character:
            await db.delete(db_character)
            await db.commit()
        return db_character

character_service = CharacterService() 