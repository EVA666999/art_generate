"""
Универсальный скрипт для обновления персонажей из файлов в БД.
"""
import asyncio
import sys
import os
import argparse

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from app.chat_bot.utils.character_importer import character_importer
from app.database.db import async_session_maker


async def update_character(character_name: str, overwrite: bool = True):
    """
    Обновляет персонажа из файла в БД.
    
    Args:
        character_name: Имя персонажа (без расширения .py)
        overwrite: Перезаписать существующего персонажа
    """
    print(f"🔄 Обновление персонажа '{character_name}'...")
    
    # Проверяем, существует ли файл персонажа
    characters_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models/characters")
    file_path = os.path.join(characters_dir, f"{character_name}.py")
    
    if not os.path.exists(file_path):
        print(f"[ERROR] Файл персонажа не найден: {file_path}")
        return False
    
    print(f"📁 Файл найден: {file_path}")
    
    async with async_session_maker() as db:
        try:
            # Импортируем персонажа
            db_char = await character_importer.import_character_to_db(
                character_name, db, overwrite=overwrite
            )
            
            if db_char:
                print(f"[OK] Персонаж '{db_char.name}' успешно обновлен!")
                print(f"   ID: {db_char.id}")
                return True
            else:
                print(f"[ERROR] Ошибка обновления персонажа '{character_name}'")
                return False
                
        except Exception as e:
            print(f"[ERROR] Ошибка: {str(e)}")
            return False


async def list_available_characters():
    """Показывает список доступных персонажей."""
    print("📁 Доступные персонажи:")
    
    characters = character_importer.list_available_characters()
    
    if not characters:
        print("   Нет доступных персонажей")
        return
    
    for i, char in enumerate(characters, 1):
        print(f"   {i}. {char}")
    
    print(f"\nВсего: {len(characters)} персонажей")


async def main():
    """Главная функция."""
    parser = argparse.ArgumentParser(description="Обновление персонажей из файлов в БД")
    parser.add_argument(
        "character_name", 
        nargs="?", 
        help="Имя персонажа для обновления (без расширения .py)"
    )
    parser.add_argument(
        "--list", "-l", 
        action="store_true", 
        help="Показать список доступных персонажей"
    )
    parser.add_argument(
        "--no-overwrite", 
        action="store_true", 
        help="Не перезаписывать существующего персонажа"
    )
    
    args = parser.parse_args()
    
    if args.list:
        await list_available_characters()
        return
    
    if not args.character_name:
        print("[ERROR] Укажите имя персонажа или используйте --list для просмотра списка")
        print("\nПримеры использования:")
        print("  python update_character.py anna")
        print("  python update_character.py --list")
        print("  python update_character.py new_char --no-overwrite")
        return
    
    success = await update_character(
        args.character_name, 
        overwrite=not args.no_overwrite
    )
    
    if success:
        print("🎉 Обновление завершено успешно!")
    else:
        print("💥 Обновление завершено с ошибками!")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main()) 