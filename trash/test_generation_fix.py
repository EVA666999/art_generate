#!/usr/bin/env python3
"""
Тест для проверки исправленной генерации ответов через text-generation-webui API.
"""

import asyncio
import sys
import os

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.textgen_webui_service import TextGenWebUIService
from app.chat_bot.config.chat_config import chat_config
from app.chat_bot.schemas.chat import ChatMessage, MessageRole


class MockCharacterConfig:
    """Мок конфигурации персонажа для тестирования"""
    def __init__(self, name="Anna", instructions=None, system_prompt=None, response_format=None):
        self.name = name
        self.instructions = instructions
        self.system_prompt = system_prompt
        self.response_format = response_format


async def test_generation():
    """Тестирует генерацию ответов через text-generation-webui API"""
    print("🔍 Тестирование генерации ответов через text-generation-webui API")
    print(f"📋 Конфигурация:")
    print(f"   Host: {chat_config.textgen_webui_host}")
    print(f"   Port: {chat_config.textgen_webui_port}")
    print(f"   URL: {chat_config.textgen_webui_url}")
    print()
    
    # Создаем сервис
    service = TextGenWebUIService()
    print(f"🔗 Сервис создан с URL: {service.base_url}")
    print()
    
    # Проверяем подключение
    print("🔍 Проверка подключения...")
    is_connected = await service.check_connection()
    if not is_connected:
        print("❌ Нет подключения к API, пропускаем тест генерации")
        await service.close()
        return
    
    print("✅ Подключение установлено")
    print()
    
    # Создаем тестовый персонаж с более четкими инструкциями
    character_config = MockCharacterConfig(
        name="Anna",
        instructions="Ты - Анна, дружелюбная и умная девушка. Ты всегда отвечаешь на вопросы пользователей. Отвечай кратко, но информативно.",
        system_prompt="Ты - Анна, помощник пользователей. Отвечай вежливо и по делу.",
        response_format="Отвечай от первого лица, как Анна. Не используй кавычки в начале и конце ответа."
    )
    
    # Создаем тестовое сообщение
    messages = [
        ChatMessage(role=MessageRole.USER, content="Привет! Как дела?", timestamp=None)
    ]
    
    print("🧪 Тестируем генерацию ответа...")
    print(f"📝 Сообщение: {messages[0].content}")
    print(f"👤 Персонаж: {character_config.name}")
    print()
    
    try:
        # Генерируем ответ
        response, raw_data = await service.generate_response(
            messages=messages,
            character_config=character_config,
            max_tokens=150,  # Увеличиваем для лучшего ответа
            temperature=0.8,  # Немного увеличиваем креативность
            top_p=0.9,
            top_k=40
        )
        
        print("✅ Генерация завершена!")
        print(f"📤 Ответ: '{response}'")
        print(f"📏 Длина ответа: {len(response)} символов")
        print(f"📊 Сырые данные: {raw_data}")
        
        # Проверяем качество ответа
        if not response.strip():
            print("❌ ПРОБЛЕМА: Ответ пустой!")
        elif len(response.strip()) < 10:
            print("⚠️ ВНИМАНИЕ: Ответ слишком короткий!")
        else:
            print("✅ Ответ выглядит нормально")
            
    except Exception as e:
        print(f"❌ Ошибка генерации: {e}")
        import traceback
        traceback.print_exc()
    
    print()
    
    # Закрываем сессию
    await service.close()
    print("🔒 Сессия закрыта")


if __name__ == "__main__":
    print("🚀 Запуск теста генерации...")
    print("=" * 50)
    
    try:
        asyncio.run(test_generation())
    except KeyboardInterrupt:
        print("\n⏹️ Тест прерван пользователем")
    except Exception as e:
        print(f"\n💥 Ошибка теста: {e}")
        import traceback
        traceback.print_exc()
    
    print("=" * 50)
    print("🏁 Тест завершен")
