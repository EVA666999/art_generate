#!/usr/bin/env python3
"""
Финальный тест для проверки всех исправлений.
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


async def test_final_solution():
    """Тестирует финальное решение"""
    
    print("🧪 Финальный тест всех исправлений...")
    print(f"📊 Конфигурация:")
    print(f"   • ENFORCE_MIN_TOKENS: {chat_config.ENFORCE_MIN_TOKENS}")
    print(f"   • MIN_NEW_TOKENS: {chat_config.MIN_NEW_TOKENS}")
    print(f"   • DEFAULT_MAX_TOKENS: {chat_config.DEFAULT_MAX_TOKENS}")
    print()
    
    # Создаем тестовый персонаж с очень агрессивными инструкциями
    test_character = CharacterConfig(
        name="TestAnna",
        instructions=(
            "You are Anna, a shy but curious young woman. "
            "CRITICAL: You MUST write responses that are AT LEAST 200-300 characters long. "
            "NEVER give short answers. Always elaborate, add details, describe feelings, "
            "include physical reactions, and ask follow-up questions. "
            "Your responses should be substantial and engaging. "
            "Continue writing until you reach at least 200 characters."
        ),
        system_prompt=(
            "You are having a conversation with your brother. "
            "IMPORTANT: Write detailed, long responses. "
            "Minimum 200 characters per response. "
            "Use descriptive language and include emotions."
        ),
        response_format=(
            "Respond naturally and in detail. "
            "Always write at least 200 characters. "
            "Include emotions, physical sensations, and detailed descriptions. "
            "Ask questions to continue the conversation."
        )
    )
    
    # Создаем тестовое сообщение с явным требованием длинного ответа
    test_message = ChatMessage(
        role=MessageRole.USER, 
        content=(
            "Hello! I want you to tell me about your day in great detail. "
            "Please write a long, detailed response with at least 200 characters. "
            "Describe everything you did, how you felt, what you thought about, "
            "and include specific details about your experiences. "
            "Make sure your response is at least 200 characters long."
        )
    )
    
    try:
        async with TextGenWebUIService() as service:
            # Проверяем соединение
            if not await service.check_connection():
                print("❌ Не удалось подключиться к text-generation-webui")
                return
            
            print("✅ Подключение к text-generation-webui установлено")
            print()
            
            # Тест 1: С обновленными настройками
            print("🔄 Тест 1: Обновленные настройки (min_tokens + ban_eos_token)")
            response1, meta1 = await service.generate_response(
                messages=[test_message],
                character_config=test_character,
                max_tokens=600,
                temperature=0.7,
                top_p=0.9,
                top_k=40,
                repeat_penalty=1.1
            )
            print(f"   • Ответ: {response1[:150]}...")
            print(f"   • Длина: {len(response1)} символов")
            print(f"   • Токены использовано: {meta1.get('tokens_used', 'неизвестно')}")
            print(f"   • Параметры: {meta1.get('generation_params', {})}")
            print()
            
            # Тест 2: С очень высоким max_tokens
            print("🔄 Тест 2: Высокий max_tokens (800) + низкая температура")
            response2, meta2 = await service.generate_response(
                messages=[test_message],
                character_config=test_character,
                max_tokens=800,
                temperature=0.3,
                top_p=0.95,
                top_k=30,
                repeat_penalty=1.05
            )
            print(f"   • Ответ: {response2[:150]}...")
            print(f"   • Длина: {len(response2)} символов")
            print(f"   • Токены использовано: {meta2.get('tokens_used', 'неизвестно')}")
            print()
            
            # Тест 3: С очень низкой температурой
            print("🔄 Тест 3: Очень низкая температура (0.1) для предсказуемости")
            response3, meta3 = await service.generate_response(
                messages=[test_message],
                character_config=test_character,
                max_tokens=700,
                temperature=0.1,
                top_p=0.98,
                top_k=20,
                repeat_penalty=1.02
            )
            print(f"   • Ответ: {response3[:150]}...")
            print(f"   • Длина: {len(response3)} символов")
            print(f"   • Токены использовано: {meta3.get('tokens_used', 'неизвестно')}")
            print()
            
            # Анализ результатов
            print("📊 Анализ результатов:")
            lengths = [len(response1), len(response2), len(response3)]
            print(f"   • Длины ответов: {lengths}")
            print(f"   • Средняя длина: {sum(lengths) / len(lengths):.1f}")
            print(f"   • Минимальная длина: {min(lengths)}")
            print(f"   • Максимальная длина: {max(lengths)}")
            
            if min(lengths) < 100:
                print("❌ Проблема: Ответы все еще короткие")
                print("🔍 Возможные причины:")
                print("   • Модель не поддерживает min_tokens")
                print("   • Нужно перезапустить сервер")
                print("   • Проблема в версии text-generation-webui")
            elif min(lengths) < 200:
                print("⚠️  Ответы лучше, но все еще короткие")
                print("💡 Попробуйте:")
                print("   • Увеличить max_tokens еще больше")
                print("   • Понизить temperature до 0.1")
                print("   • Изменить stop_sequence")
            else:
                print("✅ Все ответы имеют хорошую длину!")
                print("🎉 Проблема решена!")
                
    except Exception as e:
        print(f"❌ Ошибка тестирования: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("🚀 Запуск финального теста...")
    print("=" * 50)
    
    asyncio.run(test_final_solution())
    
    print("\n🏁 Тест завершен")
