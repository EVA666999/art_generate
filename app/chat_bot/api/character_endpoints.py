from typing import List, Sequence
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.chat_bot.schemas.chat import CharacterCreate, CharacterUpdate, CharacterInDB
from app.chat_bot.services.character_service import character_service
from app.database.db_depends import get_db

router = APIRouter(prefix="/api/v1/characters", tags=["Characters"])

@router.post("/", response_model=CharacterInDB)
async def create_character(character: CharacterCreate, db: AsyncSession = Depends(get_db)):
    """Создает нового персонажа в базе данных."""
    return await character_service.create_character(db=db, character=character)

@router.get("/", response_model=List[CharacterInDB])
async def read_characters(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)) -> Sequence[CharacterInDB]:
    """Получает список персонажей из базы данных."""
    characters = await character_service.get_characters(db, skip=skip, limit=limit)
    return characters

@router.get("/{character_id}", response_model=CharacterInDB)
async def read_character(character_id: int, db: AsyncSession = Depends(get_db)):
    """Получает одного персонажа по ID."""
    db_character = await character_service.get_character(db, character_id=character_id)
    if db_character is None:
        raise HTTPException(status_code=404, detail="Персонаж не найден")
    return db_character

@router.put("/{character_id}", response_model=CharacterInDB)
async def update_character(character_id: int, character: CharacterUpdate, db: AsyncSession = Depends(get_db)):
    """Обновляет существующего персонажа."""
    db_character = await character_service.update_character(db, character_id=character_id, character_update=character)
    if db_character is None:
        raise HTTPException(status_code=404, detail="Персонаж не найден")
    return db_character

@router.delete("/{character_id}", response_model=CharacterInDB)
async def delete_character(character_id: int, db: AsyncSession = Depends(get_db)):
    """Удаляет персонажа."""
    db_character = await character_service.delete_character(db, character_id=character_id)
    if db_character is None:
        raise HTTPException(status_code=404, detail="Персонаж не найден")
    return db_character 