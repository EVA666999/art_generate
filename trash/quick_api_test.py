#!/usr/bin/env python3
"""
Быстрый тест API endpoints text-generation-webui
"""

import asyncio
import aiohttp
import json
from pathlib import Path
import sys

# Добавляем корневую директорию проекта в PYTHONPATH
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.config.settings import get_settings

async def test_api_endpoints():
    """Тестирование основных API endpoints."""
    settings = get_settings()
    base_url = settings.textgen_webui_url
    
    print(f"🧪 Тестирование API endpoints: {base_url}")
    print("=" * 50)
    
    async with aiohttp.ClientSession() as session:
        
        # Тест 1: Проверка статуса модели
        print("\n1️⃣ Тест статуса модели (/api/v1/model)")
        try:
            async with session.get(f"{base_url}/api/v1/model") as response:
                print(f"   HTTP Status: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    print(f"   ✅ Ответ: {json.dumps(data, indent=2, ensure_ascii=False)}")
                else:
                    print(f"   ❌ Ошибка: {response.status}")
        except Exception as e:
            print(f"   ❌ Ошибка подключения: {e}")
            
        # Тест 2: Проверка генерации текста
        print("\n2️⃣ Тест генерации текста (/api/v1/generate)")
        try:
            test_prompt = "Привет! Как дела?"
            generation_request = {
                "prompt": test_prompt,
                "max_new_tokens": 50,
                "temperature": 0.7,
                "top_p": 0.9,
                "stream": False
            }
            
            async with session.post(
                f"{base_url}/api/v1/generate",
                json=generation_request,
                headers={"Content-Type": "application/json"}
            ) as response:
                print(f"   HTTP Status: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    print(f"   ✅ Ответ: {json.dumps(data, indent=2, ensure_ascii=False)}")
                else:
                    print(f"   ❌ Ошибка: {response.status}")
                    try:
                        error_data = await response.text()
                        print(f"   📝 Детали ошибки: {error_data}")
                    except:
                        pass
        except Exception as e:
            print(f"   ❌ Ошибка подключения: {e}")
            
        # Тест 3: Проверка доступности сервера
        print("\n3️⃣ Тест доступности сервера")
        try:
            async with session.get(f"{base_url}/") as response:
                print(f"   HTTP Status: {response.status}")
                if response.status == 200:
                    print("   ✅ Сервер доступен")
                else:
                    print(f"   ⚠️ Сервер отвечает с кодом: {response.status}")
        except Exception as e:
            print(f"   ❌ Сервер недоступен: {e}")
            
        # Тест 4: Проверка портов
        print("\n4️⃣ Проверка портов")
        import socket
        
        def check_port(port, host='127.0.0.1'):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                result = sock.connect_ex((host, port))
                sock.close()
                return result == 0
            except:
                return False
        
        api_port = 7860
        web_port = 7861
        
        print(f"   🔌 API порт {api_port}: {'✅ Открыт' if check_port(api_port) else '❌ Закрыт'}")
        print(f"   🌐 Web порт {web_port}: {'✅ Открыт' if check_port(web_port) else '❌ Закрыт'}")

async def main():
    """Основная функция."""
    print("🚀 БЫСТРЫЙ ТЕСТ API TEXT-GENERATION-WEBUI")
    print("=" * 60)
    
    await test_api_endpoints()
    
    print("\n" + "=" * 60)
    print("🏁 Тестирование завершено!")
    print("\n💡 Если есть ошибки, проверьте:")
    print("   1. Запущен ли text-generation-webui сервер?")
    print("   2. Правильные ли порты в настройках?")
    print("   3. Нет ли блокировки файрволом?")

if __name__ == "__main__":
    asyncio.run(main())
