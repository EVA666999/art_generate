#!/usr/bin/env python3
"""
Скрипт для проверки наличия персонажа Anna в базе данных.
"""

import asyncio
import sys
import os

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def check_anna_in_db():
    """Проверяет наличие Anna в базе данных."""
    
    print("🔍 Проверяем наличие Anna в базе данных...")
    
    try:
        from app.database.db import async_session_maker
        from app.chat_bot.models.models import CharacterDB
        from sqlalchemy import select
        
        async with async_session_maker() as db:
            # Проверяем всех персонажей
            result = await db.execute(select(CharacterDB).order_by(CharacterDB.name))
            characters = result.scalars().all()
            
            print(f"📊 Всего персонажей в БД: {len(characters)}")
            
            # Ищем Anna
            anna = None
            for char in characters:
                print(f"  - {char.id}: {char.name}")
                if char.name.lower() == "anna":
                    anna = char
                    print(f"    ✅ Найден персонаж Anna с ID {char.id}")
                    print(f"    📝 Instructions: {char.instructions[:100] if char.instructions else 'Нет'}...")
                    print(f"    🎭 System prompt: {char.system_prompt[:100] if char.system_prompt else 'Нет'}...")
                    print(f"    📋 Response format: {char.response_format[:100] if char.response_format else 'Нет'}...")
            
            if not anna:
                print("❌ Anna НЕ найден в базе данных!")
                print("💡 Нужно загрузить Anna через /load-file-character/anna")
            else:
                print("✅ Anna найден в базе данных!")
                
                # Проверяем API endpoint
                print("\n🌐 Проверяем API endpoint...")
                import httpx
                
                try:
                    async with httpx.AsyncClient() as client:
                        response = await client.get("http://localhost:8000/api/v1/characters/")
                        if response.status_code == 200:
                            api_characters = response.json()
                            print(f"📡 API вернул {len(api_characters)} персонажей:")
                            for char in api_characters:
                                print(f"  - {char['id']}: {char['name']}")
                                if char['name'].lower() == "anna":
                                    print(f"    ✅ Anna доступен через API с ID {char['id']}")
                        else:
                            print(f"❌ API вернул статус {response.status_code}")
                except Exception as e:
                    print(f"❌ Ошибка проверки API: {e}")
                    
    except Exception as e:
        print(f"❌ Ошибка проверки БД: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_anna_in_db())
