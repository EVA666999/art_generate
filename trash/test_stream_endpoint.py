#!/usr/bin/env python3
"""
Тест для проверки эндпоинта /stream/{character_id} с персонажем Anna.
"""

import asyncio
import httpx
import json
import sys
import os

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def test_stream_endpoint():
    """Тестирует эндпоинт /stream/{character_id} с Anna."""
    
    print("🧪 Тестируем эндпоинт /stream/{character_id} с Anna...")
    
    # Anna имеет ID 5 в БД
    character_id = 5
    message = "Привет! Как дела?"
    
    print(f"📤 Отправляем сообщение: '{message}'")
    print(f"👤 Персонаж ID: {character_id}")
    
    try:
        async with httpx.AsyncClient() as client:
            # Отправляем запрос на streaming endpoint
            response = await client.post(
                f"http://localhost:8000/api/v1/chat/stream/{character_id}",
                json={
                    "message": message,
                    "history": [],
                    "session_id": "test_session_123"
                },
                headers={"Content-Type": "application/json"}
            )
            
            print(f"📡 Статус ответа: {response.status_code}")
            print(f"📋 Заголовки: {dict(response.headers)}")
            
            if response.status_code == 200:
                print("✅ Запрос успешен!")
                print("📖 Читаем streaming ответ...")
                
                # Читаем streaming ответ
                content = response.text
                print(f"📄 Содержимое ответа ({len(content)} символов):")
                print("=" * 50)
                print(content)
                print("=" * 50)
                
                # Парсим streaming данные
                lines = content.split('\n')
                chunks = []
                
                for line in lines:
                    if line.startswith('data: '):
                        try:
                            json_str = line[6:]  # Убираем 'data: '
                            if json_str.strip():
                                data = json.loads(json_str)
                                if 'chunk' in data:
                                    chunks.append(data['chunk'])
                                    print(f"📦 Чанк: {data['chunk']}")
                                if data.get('done'):
                                    print("🏁 Получен флаг завершения")
                        except json.JSONDecodeError as e:
                            print(f"❌ Ошибка парсинга JSON: {e}")
                            print(f"   Строка: {line}")
                
                if chunks:
                    full_response = ''.join(chunks)
                    print(f"\n🎯 Полный ответ Anna: {full_response}")
                    
                    # Проверяем, что Anna отвечает как персонаж
                    if "anna" in full_response.lower() or "я" in full_response.lower():
                        print("✅ Anna отвечает как персонаж!")
                    else:
                        print("❌ Anna отвечает как обычный ассистент")
                else:
                    print("❌ Не удалось получить чанки ответа")
                    
            else:
                print(f"❌ Ошибка HTTP: {response.status_code}")
                print(f"📄 Текст ошибки: {response.text}")
                
    except httpx.RequestError as e:
        print(f"❌ Ошибка подключения: {e}")
        print("💡 Убедитесь, что FastAPI сервер запущен на http://localhost:8000")
    except Exception as e:
        print(f"❌ Непредвиденная ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_stream_endpoint())
