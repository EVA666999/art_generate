from typing import List
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from chat_bot.schemas.chat import CharacterCreate, CharacterUpdate, CharacterInDB
from chat_bot.create.character_service import character_service
from database.db_depends import get_db

router = APIRouter(prefix="/api/v1/characters", tags=["Characters"])

@router.post("/", response_model=CharacterInDB)
async def create_character(character: CharacterCreate, db: AsyncSession = Depends(get_db)):
    try:
        char = character_service.create_character(name=character.name)
        db_char = await character_service.add_to_db(char, db)
        return db_char
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[CharacterInDB])
async def read_characters(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    result = await character_service.get_characters(db, skip=skip, limit=limit)
    return result

@router.get("/{character_name}", response_model=CharacterInDB)
async def read_character(character_name: str, db: AsyncSession = Depends(get_db)):
    from chat_bot.models.models import CharacterDB
    from sqlalchemy import select
    result = await db.execute(select(CharacterDB).where(CharacterDB.name == character_name))
    db_char = result.scalar_one_or_none()
    if not db_char:
        raise HTTPException(status_code=404, detail="Персонаж не найден")
    return db_char

@router.put("/{character_name}", response_model=CharacterInDB)
async def update_character(character_name: str, character: CharacterUpdate, db: AsyncSession = Depends(get_db)):
    char = character_service.create_character(name=character_name)
    db_char = await character_service.update_in_db(char, db)
    if not db_char:
        raise HTTPException(status_code=404, detail="Персонаж не найден")
    return db_char

@router.delete("/{character_name}", response_model=CharacterInDB)
async def delete_character(character_name: str, db: AsyncSession = Depends(get_db)):
    db_char = await character_service.delete_from_db(character_name, db)
    if not db_char:
        raise HTTPException(status_code=404, detail="Персонаж не найден")
    return db_char

@router.get("/files", response_model=List[dict])
async def read_characters_from_files():
    """
    Возвращает список персонажей, загруженных только из файлов (без БД).
    """
    return character_service.list_characters() 