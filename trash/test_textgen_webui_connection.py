"""
Тестовый скрипт для проверки подключения к text-generation-webui.
"""
import asyncio
import aiohttp
import json
import sys
from pathlib import Path

# Добавляем корневую директорию проекта в PYTHONPATH
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.chat_bot.services.textgen_webui_service import TextGenWebUIService
from app.chat_bot.config.chat_config import chat_config

async def test_connection():
    """Тестирует подключение к text-generation-webui."""
    print("🔌 Тестирование подключения к text-generation-webui...")
    print(f"📍 URL: {chat_config.TEXTGEN_WEBUI_URL}")
    print(f"🤖 Модель: {chat_config.TEXTGEN_WEBUI_MODEL}")
    print()
    
    try:
        async with TextGenWebUIService() as service:
            # Проверяем соединение
            print("📡 Проверяем соединение...")
            is_connected = await service.check_connection()
            
            if is_connected:
                print("✅ Соединение установлено!")
                
                # Получаем доступные модели
                print("📋 Получаем список моделей...")
                models = await service.get_available_models()
                print(f"📚 Доступные модели: {len(models)}")
                for model in models:
                    print(f"  - {model.get('id', 'Unknown')}")
                
                # Проверяем статус модели
                print("\n📊 Проверяем статус модели...")
                status = await service.get_model_status()
                print(f"📈 Статус: {json.dumps(status, indent=2, ensure_ascii=False)}")
                
                # Тестируем генерацию
                print("\n🧪 Тестируем генерацию...")
                test_prompt = "Привет! Как дела?"
                response = await service.generate_text(
                    prompt=test_prompt,
                    max_tokens=50,
                    temperature=0.7
                )
                
                if response:
                    print(f"✅ Генерация успешна!")
                    print(f"📝 Ответ: {response}")
                else:
                    print("❌ Генерация не удалась")
                    
            else:
                print("❌ Соединение не установлено")
                
    except Exception as e:
        print(f"💥 Ошибка: {e}")
        import traceback
        traceback.print_exc()

async def test_direct_api():
    """Тестирует прямое подключение к API."""
    print("\n🔌 Тестирование прямого API подключения...")
    
    try:
        async with aiohttp.ClientSession() as session:
            # Проверяем /v1/models
            print("📡 Проверяем /v1/models...")
            async with session.get("http://localhost:5000/v1/models") as response:
                print(f"📊 Статус: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ API доступен: {json.dumps(data, indent=2, ensure_ascii=False)}")
                else:
                    print(f"❌ API недоступен: {response.status}")
                    
    except Exception as e:
        print(f"💥 Ошибка прямого API: {e}")

if __name__ == "__main__":
    print("🚀 Запуск тестов text-generation-webui...")
    print("=" * 50)
    
    # Тестируем прямое API
    asyncio.run(test_direct_api())
    
    # Тестируем через сервис
    asyncio.run(test_connection())
    
    print("\n🏁 Тестирование завершено!")
