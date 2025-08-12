#!/usr/bin/env python3
"""
Тест для проверки работы персонажа Anna с text-generation-webui.
"""

import asyncio
import sys
import os

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.chat_bot.models.characters.anna import get_character_data
from app.chat_bot.services.textgen_webui_service import TextGenWebUIService
from app.chat_bot.config.chat_config import chat_config

async def test_anna_character():
    """Тестирует персонажа Anna с text-generation-webui."""
    
    print("🧪 Тестируем персонажа Anna с text-generation-webui...")
    
    # Получаем данные персонажа
    character_data = get_character_data()
    print(f"✅ Персонаж загружен: {character_data['name']}")
    print(f"📝 Инструкции: {len(character_data['instructions'])} символов")
    print(f"🎭 Системный промпт: {len(character_data['system_prompt'])} символов")
    print(f"📋 Формат ответа: {len(character_data['response_format'])} символов")
    
    # Создаем сервис
    service = TextGenWebUIService()
    
    try:
        # Проверяем подключение
        print(f"\n🔌 Проверяем подключение к {chat_config.TEXTGEN_WEBUI_URL}...")
        connected = await service.check_connection()
        
        if not connected:
            print("❌ Не удалось подключиться к text-generation-webui")
            print("💡 Убедитесь, что сервер text-generation-webui запущен")
            return
        
        print("✅ Подключение к text-generation-webui установлено")
        
        # Проверяем доступные модели
        print("\n🔍 Проверяем доступные модели...")
        models = await service.get_available_models()
        if models:
            print(f"✅ Доступно моделей: {len(models)}")
            for model in models[:3]:  # Показываем первые 3
                print(f"   - {model.get('id', 'Unknown')}")
        else:
            print("⚠️ Не удалось получить список моделей")
        
        # Тестируем построение промпта
        print("\n📝 Тестируем построение промпта для Anna...")
        test_message = "Привет! Как дела?"
        prompt = service.build_character_prompt(
            character_data=character_data,
            user_message=test_message,
            history=[]
        )
        
        print(f"✅ Промпт построен ({len(prompt)} символов)")
        print("📋 Первые 200 символов промпта:")
        print("-" * 50)
        print(prompt[:200] + "..." if len(prompt) > 200 else prompt)
        print("-" * 50)
        
        # Тестируем генерацию текста
        print(f"\n🚀 Тестируем генерацию ответа для: '{test_message}'")
        
        response = await service.generate_text(
            prompt=prompt,
            max_tokens=chat_config.MYTHOMAX_MAX_TOKENS,
            temperature=chat_config.MYTHOMAX_TEMPERATURE,
            top_p=chat_config.MYTHOMAX_TOP_P,
            top_k=chat_config.MYTHOMAX_TOP_K,
            repeat_penalty=chat_config.MYTHOMAX_REPEAT_PENALTY,
            presence_penalty=chat_config.MYTHOMAX_PRESENCE_PENALTY
        )
        
        if response:
            print("✅ Ответ сгенерирован успешно!")
            print(f"📝 Длина ответа: {len(response)} символов")
            print("💬 Ответ:")
            print("-" * 50)
            print(response)
            print("-" * 50)
        else:
            print("❌ Не удалось сгенерировать ответ")
            
    except Exception as e:
        print(f"❌ Ошибка во время тестирования: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Закрываем соединение
        await service.disconnect()
        print("\n🔌 Соединение закрыто")

async def test_anna_streaming():
    """Тестирует streaming генерацию для персонажа Anna."""
    
    print("\n🌊 Тестируем streaming генерацию для Anna...")
    
    # Получаем данные персонажа
    character_data = get_character_data()
    
    # Создаем сервис
    service = TextGenWebUIService()
    
    try:
        # Проверяем подключение
        connected = await service.check_connection()
        if not connected:
            print("❌ Не удалось подключиться к text-generation-webui")
            return
        
        print("✅ Подключение установлено")
        
        # Тестируем streaming
        test_message = "Расскажи о себе"
        prompt = service.build_character_prompt(
            character_data=character_data,
            user_message=test_message,
            history=[]
        )
        
        print(f"🚀 Начинаем streaming генерацию для: '{test_message}'")
        
        response_parts = []
        async for chunk in service.generate_text_stream(
            prompt=prompt,
            max_tokens=chat_config.MYTHOMAX_MAX_TOKENS,
            temperature=chat_config.MYTHOMAX_TEMPERATURE,
            top_p=chat_config.MYTHOMAX_TOP_P,
            top_k=chat_config.MYTHOMAX_TOP_K,
            repeat_penalty=chat_config.MYTHOMAX_REPEAT_PENALTY,
            presence_penalty=chat_config.MYTHOMAX_PRESENCE_PENALTY
        ):
            if chunk:
                response_parts.append(chunk)
                print(f"📝 Чанк: {chunk}")
        
        if response_parts:
            full_response = "".join(response_parts)
            print(f"\n✅ Streaming завершен! Полный ответ ({len(full_response)} символов):")
            print("-" * 50)
            print(full_response)
            print("-" * 50)
        else:
            print("❌ Не удалось получить ответ через streaming")
            
    except Exception as e:
        print(f"❌ Ошибка streaming тестирования: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await service.disconnect()

if __name__ == "__main__":
    print("🧪 Тест персонажа Anna с text-generation-webui")
    print("=" * 60)
    
    # Запускаем тесты
    asyncio.run(test_anna_character())
    asyncio.run(test_anna_streaming())
    
    print("\n🏁 Тестирование завершено!")
