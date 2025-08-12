#!/usr/bin/env python3
"""
Простой тест для проверки передачи параметров генерации.
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


async def test_params():
    """Тестирует передачу параметров генерации"""
    
    print("🧪 Тест передачи параметров генерации...")
    print(f"📊 Конфигурация:")
    print(f"   • ENFORCE_MIN_TOKENS: {chat_config.ENFORCE_MIN_TOKENS}")
    print(f"   • MIN_NEW_TOKENS: {chat_config.MIN_NEW_TOKENS}")
    print(f"   • DEFAULT_MAX_TOKENS: {chat_config.DEFAULT_MAX_TOKENS}")
    print()
    
    # Создаем тестовый персонаж
    test_character = CharacterConfig(
        name="TestAnna",
        instructions="You are Anna, a shy but curious young woman. Write naturally and in detail.",
        system_prompt="You are having a conversation with your brother.",
        response_format="Respond naturally and in detail."
    )
    
    # Создаем тестовое сообщение
    test_message = ChatMessage(role=MessageRole.USER, content="Hello, how are you?")
    
    try:
        async with TextGenWebUIService() as service:
            # Проверяем соединение
            if not await service.check_connection():
                print("❌ Не удалось подключиться к text-generation-webui")
                return
            
            print("✅ Подключение к text-generation-webui установлено")
            print()
            
            # Тестируем с разными параметрами
            print("🔄 Тест 1: Без параметров (использует конфигурацию по умолчанию)")
            response1, meta1 = await service.generate_response(
                messages=[test_message],
                character_config=test_character
            )
            print(f"   • Ответ: {response1[:100]}...")
            print(f"   • Длина: {len(response1)} символов")
            print()
            
            print("🔄 Тест 2: С явными параметрами")
            response2, meta2 = await service.generate_response(
                messages=[test_message],
                character_config=test_character,
                max_tokens=200,
                temperature=0.9,
                top_p=0.99,
                top_k=100,
                repeat_penalty=1.2
            )
            print(f"   • Ответ: {response2[:100]}...")
            print(f"   • Длина: {len(response2)} символов")
            print()
            
            print("🔄 Тест 3: С минимальной длиной")
            response3, meta3 = await service.generate_response(
                messages=[test_message],
                character_config=test_character,
                max_tokens=300,
                temperature=0.7
            )
            print(f"   • Ответ: {response3[:100]}...")
            print(f"   • Длина: {len(response3)} символов")
            print()
            
            # Анализ результатов
            print("📊 Анализ результатов:")
            lengths = [len(response1), len(response2), len(response3)]
            print(f"   • Длины ответов: {lengths}")
            print(f"   • Средняя длина: {sum(lengths) / len(lengths):.1f}")
            print(f"   • Минимальная длина: {min(lengths)}")
            print(f"   • Максимальная длина: {max(lengths)}")
            
            if min(lengths) < 100:
                print("⚠️  Есть короткие ответы - проблема с min_new_tokens")
            else:
                print("✅ Все ответы имеют приемлемую длину")
                
    except Exception as e:
        print(f"❌ Ошибка тестирования: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("🚀 Запуск теста параметров генерации...")
    print("=" * 50)
    
    asyncio.run(test_params())
    
    print("\n🏁 Тест завершен")
