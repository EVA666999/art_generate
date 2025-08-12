#!/usr/bin/env python3
"""
Тест для проверки работы text-generation-webui с моделью MythoMax L2 13B.
Запускайте после запуска text-generation-webui сервера.
"""

import asyncio
import aiohttp
import json
from typing import Dict, Any

async def test_webui_connection():
    """Тестирует подключение к text-generation-webui."""
    print("🔌 Тестируем подключение к text-generation-webui...")
    
    try:
        async with aiohttp.ClientSession() as session:
            # Проверяем доступность API
            async with session.get("http://localhost:5000/v1/models") as response:
                if response.status == 200:
                    models = await response.json()
                    print(f"✅ API доступен. Модели: {models}")
                    return True
                else:
                    print(f"❌ API недоступен: {response.status}")
                    return False
                    
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        return False

async def test_model_status():
    """Тестирует статус модели."""
    print("\n🤖 Проверяем статус модели...")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:5000/v1/model") as response:
                if response.status == 200:
                    status = await response.json()
                    print(f"✅ Статус модели: {json.dumps(status, indent=2, ensure_ascii=False)}")
                    return status
                else:
                    print(f"❌ Не удалось получить статус модели: {response.status}")
                    return None
                    
    except Exception as e:
        print(f"❌ Ошибка получения статуса модели: {e}")
        return None

async def test_text_generation():
    """Тестирует генерацию текста."""
    print("\n📝 Тестируем генерацию текста...")
    
    try:
        # Строим промпт в формате Alpaca для MythoMax
        system_message = "Ты полезный ассистент. Отвечай кратко и по делу."
        user_message = "Привет! Как дела?"
        
        prompt = f"{system_message}\n\n### Instruction:\n{user_message}\n\n### Response:\n"
        
        payload = {
            "prompt": prompt,
            "max_new_tokens": 100,
            "temperature": 0.8,
            "top_p": 0.9,
            "top_k": 40,
            "repeat_penalty": 1.1,
            "presence_penalty": 0.1,
            "do_sample": True,
            "stream": False
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post("http://localhost:5000/v1/generate", json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    generated_text = result.get("results", [{}])[0].get("text", "")
                    
                    # Очищаем промпт из ответа
                    if generated_text.startswith(prompt):
                        generated_text = generated_text[len(prompt):].strip()
                    
                    print(f"✅ Текст сгенерирован успешно!")
                    print(f"📝 Ответ: {generated_text}")
                    return generated_text
                else:
                    print(f"❌ Ошибка генерации: {response.status}")
                    error_text = await response.text()
                    print(f"🔍 Детали ошибки: {error_text}")
                    return None
                    
    except Exception as e:
        print(f"❌ Ошибка генерации текста: {e}")
        return None

async def test_stream_generation():
    """Тестирует потоковую генерацию текста."""
    print("\n🌊 Тестируем потоковую генерацию...")
    
    try:
        system_message = "Ты полезный ассистент. Расскажи короткую историю."
        user_message = "Расскажи историю про кота"
        
        prompt = f"{system_message}\n\n### Instruction:\n{user_message}\n\n### Response:\n"
        
        payload = {
            "prompt": prompt,
            "max_new_tokens": 150,
            "temperature": 0.8,
            "top_p": 0.9,
            "top_k": 40,
            "repeat_penalty": 1.1,
            "presence_penalty": 0.1,
            "do_sample": True,
            "stream": True
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post("http://localhost:5000/v1/generate", json=payload) as response:
                if response.status == 200:
                    print("✅ Потоковая генерация началась:")
                    print("📝 Ответ:")
                    
                    full_response = ""
                    async for line in response.content:
                        if line:
                            try:
                                data = json.loads(line.decode('utf-8'))
                                if data.get("type") == "text":
                                    chunk = data.get("text", "")
                                    if chunk:
                                        print(chunk, end="", flush=True)
                                        full_response += chunk
                                elif data.get("type") == "end":
                                    print("\n✅ Потоковая генерация завершена")
                                    break
                            except json.JSONDecodeError:
                                continue
                    
                    print(f"\n📊 Полный ответ ({len(full_response)} символов): {full_response}")
                    return full_response
                else:
                    print(f"❌ Ошибка потоковой генерации: {response.status}")
                    return None
                    
    except Exception as e:
        print(f"❌ Ошибка потоковой генерации: {e}")
        return None

async def main():
    """Основная функция тестирования."""
    print("🚀 Тестирование text-generation-webui с MythoMax L2 13B")
    print("=" * 60)
    
    # Тест 1: Подключение
    if not await test_webui_connection():
        print("\n❌ Не удалось подключиться к text-generation-webui")
        print("💡 Убедитесь, что сервер запущен: start_webui_with_api.bat")
        return
    
    # Тест 2: Статус модели
    await test_model_status()
    
    # Тест 3: Генерация текста
    await test_text_generation()
    
    # Тест 4: Потоковая генерация
    await test_stream_generation()
    
    print("\n🎉 Тестирование завершено!")

if __name__ == "__main__":
    asyncio.run(main())
