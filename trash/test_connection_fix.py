#!/usr/bin/env python3
"""
Тест подключения к text-generation-webui на порту 7860.
"""
import asyncio
import aiohttp
import json

async def test_connection():
    """Тестирует подключение к text-generation-webui на порту 5000."""
    print("🔌 Тестирование подключения к text-generation-webui...")
    print("📍 URL: http://localhost:5000")
    print()
    
    try:
        async with aiohttp.ClientSession() as session:
            # Проверяем /v1/models
            print("📡 Проверяем /v1/models...")
            async with session.get("http://localhost:5000/v1/models") as response:
                print(f"📊 Статус: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ API доступен: {json.dumps(data, indent=2, ensure_ascii=False)}")
                    return True
                else:
                    print(f"❌ API недоступен: {response.status}")
                    return False
                    
    except Exception as e:
        print(f"💥 Ошибка подключения: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Тест подключения к порту 5000...")
    print("=" * 40)
    
    result = asyncio.run(test_connection())
    
    if result:
        print("\n✅ Подключение успешно!")
        print("🎯 Теперь ваш чат должен работать!")
    else:
        print("\n❌ Подключение не удалось")
        print("🔍 Проверьте, что text-generation-webui запущен")
