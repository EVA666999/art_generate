#!/usr/bin/env python3
"""
Тест для проверки персонажей в базе данных.
"""
import asyncio
import sys
import os

# Добавляем путь к проекту
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.database.db import async_session_maker
from app.chat_bot.models.models import CharacterDB
from sqlalchemy import select


async def test_characters():
    """Тестирует загрузку персонажей из базы данных."""
    print("🧪 Тестируем загрузку персонажей из БД...")
    
    try:
        async with async_session_maker() as db:
            # Получаем всех персонажей
            result = await db.execute(select(CharacterDB).order_by(CharacterDB.name))
            characters = result.scalars().all()
            
            print(f"✅ Найдено персонажей: {len(characters)}")
            
            if characters:
                print("\n📋 Список персонажей:")
                for char in characters:
                    print(f"  - ID: {char.id}, Имя: {char.name}")
                    print(f"    Instructions: {char.instructions[:50] if char.instructions else 'Нет'}...")
                    print(f"    System prompt: {char.system_prompt[:50] if char.system_prompt else 'Нет'}...")
                    print(f"    Response format: {char.response_format[:50] if char.response_format else 'Нет'}...")
                    print()
            else:
                print("❌ Персонажи не найдены в базе данных")
                
    except Exception as e:
        print(f"❌ Ошибка при загрузке персонажей: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_characters())
