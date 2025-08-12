#!/usr/bin/env python3
"""
Тест для проверки исправленного API с персонажем Anna.
"""

import asyncio
import sys
import os
import aiohttp
import json

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.chat_bot.models.characters.anna import get_character_data

async def test_api_with_anna():
    """Тестирует API с персонажем Anna."""
    
    print("🧪 Тестируем исправленный API с персонажем Anna...")
    
    # Получаем данные персонажа
    character_data = get_character_data()
    print(f"✅ Персонаж загружен: {character_data['name']}")
    
    # Тестируем API endpoint
    api_url = "http://localhost:8000/api/v1/chat/stream/5"  # character_id=5
    
    test_message = "Привет! Как дела?"
    
    payload = {
        "message": test_message,
        "history": []
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            print(f"\n🚀 Отправляем запрос к API: {api_url}")
            print(f"📝 Сообщение: {test_message}")
            
            async with session.post(api_url, json=payload) as response:
                print(f"📊 Статус ответа: {response.status}")
                
                if response.status == 200:
                    print("✅ API ответил успешно!")
                    
                    # Читаем streaming ответ
                    response_text = ""
                    async for line in response.content:
                        line_str = line.decode('utf-8').strip()
                        if line_str.startswith('data: '):
                            try:
                                data = json.loads(line_str[6:])
                                if 'chunk' in data:
                                    chunk = data['chunk']
                                    response_text += chunk
                                    print(f"📝 Чанк: {chunk}")
                                    
                                    if data.get('done', False):
                                        break
                            except json.JSONDecodeError:
                                continue
                    
                    print(f"\n💬 Полный ответ ({len(response_text)} символов):")
                    print("-" * 50)
                    print(response_text)
                    print("-" * 50)
                    
                    # Проверяем, что ответ содержит характерные для Anna элементы
                    if "I" in response_text or "my" in response_text.lower():
                        print("✅ Ответ содержит характерные для Anna элементы (первое лицо)")
                    else:
                        print("⚠️ Ответ не содержит характерных для Anna элементов")
                        
                else:
                    error_text = await response.text()
                    print(f"❌ API вернул ошибку: {response.status}")
                    print(f"📝 Текст ошибки: {error_text}")
                    
    except Exception as e:
        print(f"❌ Ошибка при тестировании API: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🧪 Тест исправленного API с персонажем Anna")
    print("=" * 60)
    
    # Запускаем тест
    asyncio.run(test_api_with_anna())
    
    print("\n🏁 Тестирование завершено!")
