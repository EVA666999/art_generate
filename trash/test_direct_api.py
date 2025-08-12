#!/usr/bin/env python3
"""
Тест прямого обращения к API text-generation-webui для проверки min_new_tokens.
"""

import asyncio
import aiohttp
import json
import random


async def test_direct_api():
    """Тестирует API напрямую"""
    
    print("🧪 Тест прямого API text-generation-webui...")
    print("🔗 URL: http://localhost:5000")
    print()
    
    # Простой промпт для теста
    test_prompt = "Hello! Please tell me about your day in detail. Write at least 200 characters."
    
    # Тест 1: Без min_new_tokens
    print("🔄 Тест 1: Без min_new_tokens")
    payload1 = {
        "prompt": test_prompt,
        "max_new_tokens": 300,
        "temperature": 0.7,
        "top_p": 0.9,
        "top_k": 40,
        "repetition_penalty": 1.1,
        "stream": False,
        "seed": random.randint(1, 999999999)
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "http://localhost:5000/v1/completions",
                json=payload1,
                headers={"Content-Type": "application/json"}
            ) as resp:
                if resp.status == 200:
                    data1 = await resp.json()
                    response1 = data1["choices"][0]["text"].strip()
                    print(f"   • Ответ: {response1[:100]}...")
                    print(f"   • Длина: {len(response1)} символов")
                    print(f"   • Токены: {data1.get('usage', {}).get('total_tokens', 'неизвестно')}")
                else:
                    print(f"   • Ошибка: {resp.status}")
                    text = await resp.text()
                    print(f"   • Детали: {text}")
    except Exception as e:
        print(f"   • Ошибка: {e}")
    
    print()
    
    # Тест 2: С min_new_tokens
    print("🔄 Тест 2: С min_new_tokens=100")
    payload2 = {
        "prompt": test_prompt,
        "max_new_tokens": 300,
        "min_new_tokens": 100,
        "temperature": 0.7,
        "top_p": 0.9,
        "top_k": 40,
        "repetition_penalty": 1.1,
        "stream": False,
        "seed": random.randint(1, 999999999)
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "http://localhost:5000/v1/completions",
                json=payload2,
                headers={"Content-Type": "application/json"}
            ) as resp:
                if resp.status == 200:
                    data2 = await resp.json()
                    response2 = data2["choices"][0]["text"].strip()
                    print(f"   • Ответ: {response2[:100]}...")
                    print(f"   • Длина: {len(response2)} символов")
                    print(f"   • Токены: {data2.get('usage', {}).get('total_tokens', 'неизвестно')}")
                else:
                    print(f"   • Ошибка: {resp.status}")
                    text = await resp.text()
                    print(f"   • Детали: {text}")
    except Exception as e:
        print(f"   • Ошибка: {e}")
    
    print()
    
    # Тест 3: С очень высоким min_new_tokens
    print("🔄 Тест 3: С min_new_tokens=200")
    payload3 = {
        "prompt": test_prompt,
        "max_new_tokens": 500,
        "min_new_tokens": 200,
        "temperature": 0.7,
        "top_p": 0.9,
        "top_k": 40,
        "repetition_penalty": 1.1,
        "stream": False,
        "seed": random.randint(1, 999999999)
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "http://localhost:5000/v1/completions",
                json=payload3,
                headers={"Content-Type": "application/json"}
            ) as resp:
                if resp.status == 200:
                    data3 = await resp.json()
                    response3 = data3["choices"][0]["text"].strip()
                    print(f"   • Ответ: {response3[:100]}...")
                    print(f"   • Длина: {len(response3)} символов")
                    print(f"   • Токены: {data3.get('usage', {}).get('total_tokens', 'неизвестно')}")
                else:
                    print(f"   • Ошибка: {resp.status}")
                    text = await resp.text()
                    print(f"   • Детали: {text}")
    except Exception as e:
        print(f"   • Ошибка: {e}")
    
    print()
    
    # Проверяем информацию о модели
    print("🔍 Информация о модели:")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:5000/v1/models") as resp:
                if resp.status == 200:
                    models = await resp.json()
                    for model in models.get("data", []):
                        print(f"   • Модель: {model.get('id', 'неизвестно')}")
                        print(f"     - Поддерживаемые параметры: {list(model.keys())}")
                else:
                    print(f"   • Ошибка получения моделей: {resp.status}")
    except Exception as e:
        print(f"   • Ошибка: {e}")


if __name__ == "__main__":
    print("🚀 Запуск теста прямого API...")
    print("=" * 50)
    
    asyncio.run(test_direct_api())
    
    print("\n🏁 Тест завершен")
