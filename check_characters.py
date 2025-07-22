#!/usr/bin/env python3
"""
Скрипт для проверки персонажей в системе
"""
import asyncio
import sys
import os

# Добавляем путь к app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

async def check_characters():
    """Проверяет персонажей в системе"""
    print("🔍 Проверка персонажей в системе...")
    
    # 1. Проверяем персонажей из файлов
    print("\n📁 Персонажи из файлов:")
    try:
        from app.chat_bot.create.character_service import character_service
        file_characters = character_service.list_characters()
        for char in file_characters:
            print(f"  - {char['name']}: {char['personality'][:50]}...")
    except Exception as e:
        print(f"  ❌ Ошибка загрузки из файлов: {e}")
    
    # 2. Проверяем персонажей из БД
    print("\n🗄️ Персонажи из базы данных:")
    try:
        from app.database.db import get_db
        from app.chat_bot.models.models import CharacterDB
        from sqlalchemy import select
        
        async for db in get_db():
            result = await db.execute(select(CharacterDB))
            db_characters = result.scalars().all()
            
            if db_characters:
                for char in db_characters:
                    print(f"  - {char.name}: {char.personality[:50]}...")
            else:
                print("  📭 База данных пуста")
            break
    except Exception as e:
        print(f"  ❌ Ошибка загрузки из БД: {e}")
    
    # 3. Проверяем API endpoint
    print("\n🌐 Проверка API endpoint:")
    try:
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/api/characters/")
            if response.status_code == 200:
                api_characters = response.json()
                print(f"  ✅ API вернул {len(api_characters)} персонажей:")
                for char in api_characters:
                    print(f"    - {char['name']}")
            else:
                print(f"  ❌ API вернул статус {response.status_code}")
    except Exception as e:
        print(f"  ❌ Ошибка API: {e}")

if __name__ == "__main__":
    asyncio.run(check_characters()) 