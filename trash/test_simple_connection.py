#!/usr/bin/env python3
"""
Простой тест асинхронного подключения для диагностики.
"""

import asyncio
import aiohttp
from aiohttp import ClientTimeout


async def test_simple_connection():
    """Простой тест асинхронного подключения"""
    print("🔍 Простой тест асинхронного подключения")
    
    # Создаем сессию
    session = aiohttp.ClientSession()
    
    try:
        print("📡 Тестируем подключение к http://127.0.0.1:7860/")
        
        # Тест 1: Простой GET запрос
        async with session.get("http://127.0.0.1:7860/", timeout=ClientTimeout(total=10)) as resp:
            print(f"✅ GET запрос успешен: статус {resp.status}")
            text = await resp.text()
            print(f"📝 Ответ: {text[:100]}...")
        
        # Тест 2: POST запрос к API
        print("\n📡 Тестируем POST запрос к /api/v1/generate")
        test_payload = {
            "prompt": "Hello",
            "max_new_tokens": 10,
            "temperature": 0.7
        }
        
        async with session.post("http://127.0.0.1:7860/api/v1/generate", 
                               json=test_payload, 
                               timeout=ClientTimeout(total=30)) as resp:
            print(f"✅ POST запрос успешен: статус {resp.status}")
            if resp.status == 200:
                data = await resp.json()
                print(f"📊 Ответ: {data}")
            else:
                text = await resp.text()
                print(f"📝 Ошибка: {text}")
                
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await session.close()
        print("🔒 Сессия закрыта")


if __name__ == "__main__":
    print("🚀 Запуск простого теста...")
    print("=" * 50)
    
    try:
        asyncio.run(test_simple_connection())
    except Exception as e:
        print(f"💥 Ошибка: {e}")
        import traceback
        traceback.print_exc()
    
    print("=" * 50)
    print("🏁 Тест завершен")
