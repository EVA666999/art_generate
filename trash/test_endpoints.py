#!/usr/bin/env python3
"""
Тест доступных endpoints в text-generation-webui
"""

import asyncio
import aiohttp
import json
import sys
from pathlib import Path

# Добавляем корень проекта в PYTHONPATH
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

async def test_endpoints():
    """Тестирует различные endpoints text-generation-webui"""
    base_url = "http://localhost:5000"
    
    async with aiohttp.ClientSession() as session:
        # Тест 1: /v1/models
        print("🔍 Тестирую /v1/models...")
        try:
            async with session.get(f"{base_url}/v1/models") as response:
                print(f"   Статус: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    print(f"   Ответ: {json.dumps(data, indent=2, ensure_ascii=False)}")
                else:
                    print(f"   Ошибка: {response.status}")
        except Exception as e:
            print(f"   ❌ Ошибка: {e}")
        
        print()
        
        # Тест 2: /v1/chat/completions
        print("🔍 Тестирую /v1/chat/completions...")
        try:
            payload = {
                "model": "Gryphe-MythoMax-L2-13b.Q4_K_S.gguf",
                "messages": [{"role": "user", "content": "Привет"}],
                "max_tokens": 10
            }
            async with session.post(f"{base_url}/v1/chat/completions", json=payload) as response:
                print(f"   Статус: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    print(f"   Ответ: {json.dumps(data, indent=2, ensure_ascii=False)}")
                else:
                    print(f"   Ошибка: {response.status}")
                    try:
                        error_text = await response.text()
                        print(f"   Детали ошибки: {error_text}")
                    except:
                        pass
        except Exception as e:
            print(f"   ❌ Ошибка: {e}")
        
        print()
        
        # Тест 3: /v1/generate (старый endpoint)
        print("🔍 Тестирую /v1/generate...")
        try:
            payload = {
                "prompt": "Привет",
                "max_new_tokens": 10,
                "temperature": 0.7,
                "do_sample": True
            }
            async with session.post(f"{base_url}/v1/generate", json=payload) as response:
                print(f"   Статус: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    print(f"   Ответ: {json.dumps(data, indent=2, ensure_ascii=False)}")
                else:
                    print(f"   Ошибка: {response.status}")
                    try:
                        error_text = await response.text()
                        print(f"   Детали ошибки: {error_text}")
                    except:
                        pass
        except Exception as e:
            print(f"   ❌ Ошибка: {e}")
        
        print()
        
        # Тест 4: /api/v1/generate (альтернативный endpoint)
        print("🔍 Тестирую /api/v1/generate...")
        try:
            payload = {
                "prompt": "Привет",
                "max_new_tokens": 10,
                "temperature": 0.7,
                "do_sample": True
            }
            async with session.post(f"{base_url}/api/v1/generate", json=payload) as response:
                print(f"   Статус: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    print(f"   Ответ: {json.dumps(data, indent=2, ensure_ascii=False)}")
                else:
                    print(f"   Ошибка: {response.status}")
                    try:
                        error_text = await response.text()
                        print(f"   Детали ошибки: {error_text}")
                    except:
                        pass
        except Exception as e:
            print(f"   ❌ Ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(test_endpoints())
