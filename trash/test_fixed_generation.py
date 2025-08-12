#!/usr/bin/env python3
"""
Тестовый скрипт для проверки исправлений с минимальной длиной токенов.
"""

import asyncio
import sys
from pathlib import Path

# Добавляем корневую директорию проекта в PYTHONPATH
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.chat_bot.services.textgen_webui_service import TextGenWebUIService
from app.chat_bot.schemas.chat import ChatMessage, MessageRole, CharacterConfig
from app.chat_bot.config.chat_config import chat_config


async def test_fixed_generation():
    """Тестирует исправленную генерацию с минимальной длиной токенов"""
    
    print("🧪 Тестирование ИСПРАВЛЕННОЙ генерации...")
    print(f"📊 Конфигурация:")
    print(f"   • DEFAULT_MAX_TOKENS: {chat_config.DEFAULT_MAX_TOKENS}")
    print(f"   • DEFAULT_TEMPERATURE: {chat_config.DEFAULT_TEMPERATURE}")
    print(f"   • DEFAULT_TOP_P: {chat_config.DEFAULT_TOP_P}")
    print(f"   • DEFAULT_TOP_K: {chat_config.DEFAULT_TOP_K}")
    print(f"   • DEFAULT_REPEAT_PENALTY: {chat_config.DEFAULT_REPEAT_PENALTY}")
    print(f"   • DEFAULT_PRESENCE_PENALTY: {chat_config.DEFAULT_PRESENCE_PENALTY}")
    print(f"   • ENFORCE_MIN_TOKENS: {chat_config.ENFORCE_MIN_TOKENS}")
    print(f"   • MIN_NEW_TOKENS: {chat_config.MIN_NEW_TOKENS}")
    print(f"   • BAN_EOS_TOKEN: {chat_config.BAN_EOS_TOKEN}")
    print(f"   • DEFAULT_STOP_TOKENS: {chat_config.DEFAULT_STOP_TOKENS}")
    print()
    
    # Создаем тестовый персонаж
    test_character = CharacterConfig(
        name="TestAnna",
        instructions="You are Anna, a shy but curious young woman. Write naturally and in detail.",
        system_prompt="You are having a conversation with your brother.",
        response_format="Respond naturally and in detail."
    )
    
    # Тестовые сообщения
    test_messages = [
        ChatMessage(
            role=MessageRole.USER,
            content="Tell me about your day and what you've been thinking about."
        )
    ]
    
    try:
        async with TextGenWebUIService() as service:
            # Проверяем соединение
            if not await service.check_connection():
                print("❌ Не удалось подключиться к text-generation-webui")
                return
            
            print("✅ Подключение к text-generation-webui установлено")
            print()
            
            # Тестируем генерацию
            print("🔄 Генерирую ответ...")
            response, meta = await service.generate_response(
                messages=test_messages,
                character_config=test_character,
                temperature=0.8,
                max_tokens=1024
            )
            
            print(f"📝 Ответ получен:")
            print(f"   • Длина: {len(response)} символов")
            print(f"   • Токены использовано: {meta.get('tokens_used', 'неизвестно')}")
            print(f"   • Модель: {meta.get('model_data', {}).get('model', 'неизвестно')}")
            print()
            print("📄 Текст ответа:")
            print("-" * 50)
            print(response)
            print("-" * 50)
            
            # Анализируем качество
            if len(response) < 100:
                print("⚠️  ВНИМАНИЕ: Ответ все еще слишком короткий!")
                print("🔍 Возможные причины:")
                print("   • Модель не поддерживает min_new_tokens")
                print("   • Проблема с самим MythoMax")
                print("   • Нужно попробовать другую модель")
            elif len(response) < 200:
                print("⚠️  Ответ короткий, но лучше")
            else:
                print("✅ Ответ имеет хорошую длину!")
                
    except Exception as e:
        print(f"❌ Ошибка тестирования: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("🚀 Запуск теста ИСПРАВЛЕННОЙ генерации...")
    print("=" * 50)
    
    asyncio.run(test_fixed_generation())
    
    print("\n🏁 Тест завершен")
