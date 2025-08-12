#!/usr/bin/env python3
"""
Тест альтернативных параметров для обхода проблемы min_new_tokens.
"""

import asyncio
import aiohttp
import json
import random


async def test_alternative_params():
    """Тестирует альтернативные параметры"""
    
    print("🧪 Тест альтернативных параметров...")
    print("🔗 URL: http://localhost:5000")
    print()
    
    # Промпт с явным требованием длинного ответа
    test_prompt = (
        "Hello! Please tell me about your day in detail. "
        "Write at least 200 characters. "
        "Describe everything you did, how you felt, what you thought about, "
        "and include specific details about your experiences. "
        "Continue writing until you reach at least 200 characters."
    )
    
    # Тест 1: min_tokens вместо min_new_tokens
    print("🔄 Тест 1: min_tokens=100 (вместо min_new_tokens)")
    payload1 = {
        "prompt": test_prompt,
        "max_new_tokens": 500,
        "min_tokens": 100,
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
    
    # Тест 2: С stop_sequence для принудительного продолжения
    print("🔄 Тест 2: stop_sequence для продолжения")
    payload2 = {
        "prompt": test_prompt,
        "max_new_tokens": 800,
        "temperature": 0.7,
        "top_p": 0.9,
        "top_k": 40,
        "repetition_penalty": 1.1,
        "stop": ["\n\n", ".", "!", "?"],  # Останавливаемся только на двойных переносах
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
    
    # Тест 3: С очень низкой температурой и высоким max_tokens
    print("🔄 Тест 3: Низкая температура + высокий max_tokens")
    payload3 = {
        "prompt": test_prompt,
        "max_new_tokens": 1000,
        "temperature": 0.1,  # Очень низкая температура для предсказуемости
        "top_p": 0.95,
        "top_k": 20,
        "repetition_penalty": 1.05,
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
    
    # Тест 4: С ban_eos_token и add_bos_token
    print("🔄 Тест 4: ban_eos_token + add_bos_token")
    payload4 = {
        "prompt": test_prompt,
        "max_new_tokens": 600,
        "temperature": 0.7,
        "top_p": 0.9,
        "top_k": 40,
        "repetition_penalty": 1.1,
        "ban_eos_token": True,  # Запрещаем EOS токен
        "add_bos_token": False,  # Не добавляем BOS токен
        "stream": False,
        "seed": random.randint(1, 999999999)
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "http://localhost:5000/v1/completions",
                json=payload4,
                headers={"Content-Type": "application/json"}
            ) as resp:
                if resp.status == 200:
                    data4 = await resp.json()
                    response4 = data4["choices"][0]["text"].strip()
                    print(f"   • Ответ: {response4[:100]}...")
                    print(f"   • Длина: {response4[:100]} символов")
                    print(f"   • Токены: {data4.get('usage', {}).get('total_tokens', 'неизвестно')}")
                else:
                    print(f"   • Ошибка: {resp.status}")
                    text = await resp.text()
                    print(f"   • Детали: {text}")
    except Exception as e:
        print(f"   • Ошибка: {e}")
    
    print()
    
    # Анализ результатов
    print("📊 Анализ результатов:")
    print("💡 Если min_tokens не работает, попробуйте:")
    print("   • Использовать stop_sequence для контроля длины")
    print("   • Увеличить max_new_tokens")
    print("   • Понизить temperature для предсказуемости")
    print("   • Использовать ban_eos_token")


if __name__ == "__main__":
    print("🚀 Запуск теста альтернативных параметров...")
    print("=" * 50)
    
    asyncio.run(test_alternative_params())
    
    print("\n🏁 Тест завершен")
