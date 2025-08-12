#!/usr/bin/env python3
"""
Тест здоровья приложения и text-generation-webui сервиса.
"""

import asyncio
import aiohttp
import json
from datetime import datetime

async def test_app_health():
    """Тестируем health check эндпоинт."""
    print("🔍 Тестируем health check приложения...")
    
    try:
        async with aiohttp.ClientSession() as session:
            # Тестируем основной health check
            async with session.get("http://localhost:8000/health") as response:
                if response.status == 200:
                    health_data = await response.json()
                    print("✅ Health check успешен:")
                    print(f"   Статус: {health_data.get('status')}")
                    print(f"   Время: {health_data.get('timestamp')}")
                    
                    # Проверяем статус text-generation-webui
                    if 'services' in health_data:
                        textgen_health = health_data['services'].get('text_generation_webui', {})
                        print(f"   TextGen WebUI: {textgen_health.get('status', 'unknown')}")
                        if 'warnings' in textgen_health:
                            print(f"   Предупреждения: {', '.join(textgen_health['warnings'])}")
                else:
                    print(f"❌ Health check неуспешен: {response.status}")
                    
    except Exception as e:
        print(f"❌ Ошибка тестирования health check: {e}")

async def test_textgen_status():
    """Тестируем статус text-generation-webui."""
    print("\n🔍 Тестируем статус text-generation-webui...")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:8000/api/v1/chat/textgen-status") as response:
                if response.status == 200:
                    status_data = await response.json()
                    print("✅ TextGen WebUI статус получен:")
                    print(f"   Доступен: {status_data.get('available')}")
                    print(f"   Модель: {status_data.get('current_model')}")
                    print(f"   Загружена: {status_data.get('model_loaded')}")
                    print(f"   Статус: {status_data.get('status')}")
                else:
                    print(f"❌ Ошибка получения статуса: {response.status}")
                    
    except Exception as e:
        print(f"❌ Ошибка тестирования TextGen WebUI: {e}")

async def test_chat_status():
    """Тестируем статус чат-сервиса."""
    print("\n🔍 Тестируем статус чат-сервиса...")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:8000/api/v1/chat/status") as response:
                if response.status == 200:
                    chat_status = await response.json()
                    print("✅ Статус чата получен:")
                    print(f"   Подключен: {chat_status.get('connected')}")
                    print(f"   Кэш: {chat_status.get('cache_enabled')}")
                    print(f"   Макс. история: {chat_status.get('max_history_length')}")
                else:
                    print(f"❌ Ошибка получения статуса чата: {response.status}")
                    
    except Exception as e:
        print(f"❌ Ошибка тестирования чат-сервиса: {e}")

async def main():
    """Основная функция тестирования."""
    print("🚀 Запуск тестов приложения...")
    print(f"⏰ Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    await test_app_health()
    await test_textgen_status()
    await test_chat_status()
    
    print("\n✅ Тестирование завершено!")

if __name__ == "__main__":
    asyncio.run(main())
