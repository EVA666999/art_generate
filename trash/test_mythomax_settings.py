#!/usr/bin/env python3
"""
Тестовый скрипт для проверки настроек MythoMax через settings.yaml.
"""

import asyncio
import sys
from pathlib import Path

# Добавляем корневую директорию проекта в PYTHONPATH
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.chat_bot.services.textgen_webui_service import TextGenWebUIService
from app.chat_bot.schemas.chat import ChatMessage, MessageRole, CharacterConfig, SimpleChatRequest
from app.chat_bot.config.chat_config import chat_config
from app.chat_bot.models.characters.anna import get_mythomax_prompt_with_user_message


async def test_mythomax_settings():
    """Тестирует настройки MythoMax через settings.yaml"""
    
    print("🧪 Тестирование настроек MythoMax через settings.yaml...")
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
    
    print("📋 Важно: Убедитесь, что text-generation-webui запущен с обновленным settings.yaml!")
    print("   • Файл: text-generation-webui/user_data/settings.yaml")
    print("   • Chat template настроен для MythoMax")
    print("   • Min tokens: 100, Max tokens: 1024")
    print()
    
    # Создаем тестовый персонаж
    test_character = CharacterConfig(
        name="TestAnna",
        instructions="You are Anna, a shy but curious young woman. Write naturally and in detail.",
        system_prompt="You are having a conversation with your brother.",
        response_format="Respond naturally and in detail."
    )
    
    # Создаем тестовый запрос С ПАРАМЕТРАМИ ГЕНЕРАЦИИ
    test_request = SimpleChatRequest(
        message="Tell me about your day and what you've been thinking about.",
        max_tokens=1024,
        temperature=0.8,
        top_p=0.95,
        top_k=50,
        repeat_penalty=1.1
    )
    
    print("📝 Тестовый запрос:")
    print(f"   • max_tokens: {test_request.max_tokens}")
    print(f"   • temperature: {test_request.temperature}")
    print(f"   • top_p: {test_request.top_p}")
    print(f"   • top_k: {test_request.top_k}")
    print(f"   • repeat_penalty: {test_request.repeat_penalty}")
    print()
    
    # Тестируем формирование промпта
    print("🔍 Тестирование формирования промпта:")
    mythomax_prompt = get_mythomax_prompt_with_user_message(test_request.message)
    print(f"   • Длина промпта: {len(mythomax_prompt)} символов")
    print(f"   • Содержит <|im_start|>: {'<|im_start|>' in mythomax_prompt}")
    print(f"   • Содержит <|im_end|>: {'<|im_end|>' in mythomax_prompt}")
    print(f"   • Содержит system: {'<|im_start|>system' in mythomax_prompt}")
    print(f"   • Содержит user: {'<|im_start|>user' in mythomax_prompt}")
    print(f"   • Содержит assistant: {'<|im_start|>assistant' in mythomax_prompt}")
    print()
    print("📄 Превью промпта:")
    print("-" * 50)
    print(mythomax_prompt[:500] + "..." if len(mythomax_prompt) > 500 else mythomax_prompt)
    print("-" * 50)
    print()
    
    try:
        async with TextGenWebUIService() as service:
            # Проверяем соединение
            if not await service.check_connection():
                print("❌ Не удалось подключиться к text-generation-webui")
                print("💡 Убедитесь, что сервер запущен с обновленным settings.yaml")
                return
            
            print("✅ Подключение к text-generation-webui установлено")
            print()
            
            # Тестируем генерацию
            print("🔄 Генерирую ответ...")
            response, meta = await service.generate_response(
                messages=[ChatMessage(role=MessageRole.USER, content=test_request.message)],
                character_config=test_character,
                max_tokens=test_request.max_tokens,
                temperature=test_request.temperature,
                top_p=test_request.top_p,
                top_k=test_request.top_k,
                repeat_penalty=test_request.repeat_penalty
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
                print("   • settings.yaml не загружен")
                print("   • Нужно перезапустить text-generation-webui")
                print("   • Модель не поддерживает min_new_tokens")
            elif len(response) < 200:
                print("⚠️  Ответ короткий, но лучше")
            else:
                print("✅ Ответ имеет хорошую длину!")
                
    except Exception as e:
        print(f"❌ Ошибка тестирования: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("🚀 Запуск теста настроек MythoMax через settings.yaml...")
    print("=" * 50)
    
    asyncio.run(test_mythomax_settings())
    
    print("\n🏁 Тест завершен")
