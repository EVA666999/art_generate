from typing import List
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.chat_bot.schemas.chat import CharacterCreate, CharacterUpdate, CharacterInDB
from app.chat_bot.utils.character_importer import character_importer
from app.database.db_depends import get_db

router = APIRouter(prefix="/api/v1/characters", tags=["Characters"])

@router.post("/", response_model=CharacterInDB)
async def create_character(character: CharacterCreate, db: AsyncSession = Depends(get_db)):
    """Создает нового персонажа в базе данных."""
    try:
        from app.chat_bot.models.models import CharacterDB
        from sqlalchemy import select
        
        # Проверяем, существует ли персонаж
        result = await db.execute(
            select(CharacterDB).where(CharacterDB.name == character.name)
        )
        existing_char = result.scalar_one_or_none()
        
        if existing_char:
            raise HTTPException(
                status_code=400, 
                detail=f"Персонаж с именем {character.name} уже существует"
            )
        
        # Создаем нового персонажа в формате Alpaca
        db_char = CharacterDB(
            name=character.name,
            instructions=character.instructions or "",
            system_prompt=character.system_prompt or "",
            response_format=character.response_format or ""
        )
        
        db.add(db_char)
        await db.commit()
        await db.refresh(db_char)
        return db_char
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[CharacterInDB])
async def read_characters(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    """Получает список персонажей из базы данных."""
    try:
        from app.chat_bot.models.models import CharacterDB
        from sqlalchemy import select
        
        result = await db.execute(
            select(CharacterDB)
            .offset(skip)
            .limit(limit)
            .order_by(CharacterDB.name)
        )
        characters = result.scalars().all()
        return characters
    except Exception as e:
        # Если база данных недоступна, возвращаем пустой список
        print(f"Ошибка загрузки персонажей из БД: {e}")
        return []

@router.get("/{character_name}", response_model=CharacterInDB)
async def read_character(character_name: str, db: AsyncSession = Depends(get_db)):
    try:
        from app.chat_bot.models.models import CharacterDB
        from sqlalchemy import select
        result = await db.execute(select(CharacterDB).where(CharacterDB.name == character_name))
        db_char = result.scalar_one_or_none()
        if not db_char:
            raise HTTPException(status_code=404, detail="Персонаж не найден")
        return db_char
    except Exception as e:
        print(f"Ошибка загрузки персонажа {character_name}: {e}")
        raise HTTPException(status_code=500, detail="Ошибка загрузки персонажа")

@router.put("/{character_name}", response_model=CharacterInDB)
async def update_character(
    character_name: str, 
    character: CharacterUpdate, 
    db: AsyncSession = Depends(get_db)
):
    """Обновляет персонажа в базе данных."""
    from app.chat_bot.models.models import CharacterDB
    from sqlalchemy import select
    
    try:
        # Находим персонажа
        result = await db.execute(
            select(CharacterDB).where(CharacterDB.name == character_name)
        )
        db_char = result.scalar_one_or_none()
        
        if not db_char:
            raise HTTPException(
                status_code=404, 
                detail=f"Персонаж {character_name} не найден"
            )
        
        # Обновляем поля Alpaca
        if character.instructions is not None:
            db_char.instructions = character.instructions
        if character.system_prompt is not None:
            db_char.system_prompt = character.system_prompt
        if character.response_format is not None:
            db_char.response_format = character.response_format
        
        await db.commit()
        await db.refresh(db_char)
        return db_char
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{character_name}", response_model=CharacterInDB)
async def delete_character(character_name: str, db: AsyncSession = Depends(get_db)):
    """Удаляет персонажа из базы данных."""
    from app.chat_bot.models.models import CharacterDB
    from sqlalchemy import select
    
    try:
        # Находим персонажа
        result = await db.execute(
            select(CharacterDB).where(CharacterDB.name == character_name)
        )
        db_char = result.scalar_one_or_none()
        
        if not db_char:
            raise HTTPException(
                status_code=404, 
                detail=f"Персонаж {character_name} не найден"
            )
        
        await db.delete(db_char)
        await db.commit()
        return db_char
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/files", response_model=List[dict])
async def read_characters_from_files():
    """Возвращает список персонажей из файлов."""
    try:
        characters = character_importer.list_available_characters()
        return [{"name": char} for char in characters]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/import/{character_name}")
async def import_character_from_file(
    character_name: str, 
    overwrite: bool = False, 
    db: AsyncSession = Depends(get_db)
):
    """
    Импортирует персонажа из файла в базу данных.
    
    Args:
        character_name: Имя персонажа (без расширения .py)
        overwrite: Перезаписать существующего персонажа
        db: Сессия базы данных
    """
    try:
        db_char = await character_importer.import_character_to_db(
            character_name, db, overwrite
        )
        if db_char:
            return {
                "message": f"Персонаж {character_name} успешно импортирован",
                "character": {
                    "id": db_char.id,
                    "name": db_char.name
                }
            }
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Не удалось импортировать персонажа {character_name}"
            )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/import-all")
async def import_all_characters(
    overwrite: bool = False, 
    db: AsyncSession = Depends(get_db)
):
    """
    Импортирует всех персонажей из файлов в базу данных.
    
    Args:
        overwrite: Перезаписать существующих персонажей
        db: Сессия базы данных
    """
    try:
        imported = await character_importer.import_all_characters(db, overwrite)
        return {
            "message": f"Импортировано {len(imported)} персонажей",
            "characters": [
                {
                    "id": char.id,
                    "name": char.name
                } for char in imported
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/available-files")
async def list_available_characters():
    """Возвращает список доступных файлов персонажей."""
    try:
        characters = character_importer.list_available_characters()
        return {
            "characters": characters,
            "count": len(characters)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) 