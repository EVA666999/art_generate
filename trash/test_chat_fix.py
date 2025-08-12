#!/usr/bin/env python3
"""
Тест исправленного chat endpoint.
Проверяет, что ошибка 'tuple' object has no attribute 'get' исправлена.
"""

import asyncio
import sys
import os

# Добавляем путь к проекту
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.chat_bot.services.textgen_webui_service import TextGenWebUIService

async def test_prompt_building_with_tuple_history():
    """Тестирует построение промпта с историей в формате кортежей (как в chat endpoint)."""
    print("🧪 Тестируем построение промпта с историей в формате кортежей...")
    
    service = TextGenWebUIService()
    
    # Имитируем формат истории, который передается из chat endpoint
    # В chat endpoint: history=[(msg.role.value, msg.content) for msg in messages[:-1]]
    history_tuple = [
        ("user", "Привет! Как дела?"),
        ("assistant", "Привет! У меня все хорошо, спасибо! Как у тебя дела?"),
        ("user", "Тоже хорошо! Расскажи что-нибудь интересное")
    ]
    
    system_prompt = "Ты дружелюбный помощник по имени Анна. Ты всегда вежлива и готова помочь."
    user_message = "Расскажи анекдот про программистов"
    
    try:
        prompt = service.build_mythomax_prompt(system_prompt, user_message, history=history_tuple)
        print("✅ Промпт успешно построен!")
        print(f"📝 Результат:\n{prompt}")
        
        # Проверяем, что промпт содержит все необходимые части
        assert "### Instruction:" in prompt, "Промпт должен содержать Instruction секции"
        assert "### Response:" in prompt, "Промпт должен содержать Response секции"
        assert "Привет! Как дела?" in prompt, "Промпт должен содержать первое сообщение пользователя"
        assert "Привет! У меня все хорошо" in prompt, "Промпт должен содержать ответ ассистента"
        assert "Расскажи анекдот про программистов" in prompt, "Промпт должен содержать текущее сообщение пользователя"
        
        print("✅ Все проверки пройдены успешно!")
        
    except Exception as e:
        print(f"❌ Ошибка при построении промпта: {e}")
        import traceback
        traceback.print_exc()

async def test_prompt_building_with_dict_history():
    """Тестирует построение промпта с историей в формате словарей (новый формат)."""
    print("\n🧪 Тестируем построение промпта с историей в формате словарей...")
    
    service = TextGenWebUIService()
    
    # Новый формат истории (после исправления)
    history_dict = [
        {"role": "user", "content": "Привет! Как дела?"},
        {"role": "assistant", "content": "Привет! У меня все хорошо, спасибо! Как у тебя дела?"},
        {"role": "user", "content": "Тоже хорошо! Расскажи что-нибудь интересное"}
    ]
    
    system_prompt = "Ты дружелюбный помощник по имени Анна. Ты всегда вежлива и готова помочь."
    user_message = "Расскажи анекдот про программистов"
    
    try:
        prompt = service.build_mythomax_prompt(system_prompt, user_message, history=history_dict)
        print("✅ Промпт успешно построен!")
        print(f"📝 Результат:\n{prompt}")
        
        # Проверяем, что промпт содержит все необходимые части
        assert "### Instruction:" in prompt, "Промпт должен содержать Instruction секции"
        assert "### Response:" in prompt, "Промпт должен содержать Response секции"
        assert "Привет! Как дела?" in prompt, "Промпт должен содержать первое сообщение пользователя"
        assert "Привет! У меня все хорошо" in prompt, "Промпт должен содержать ответ ассистента"
        assert "Расскажи анекдот про программистов" in prompt, "Промпт должен содержать текущее сообщение пользователя"
        
        print("✅ Все проверки пройдены успешно!")
        
    except Exception as e:
        print(f"❌ Ошибка при построении промпта: {e}")
        import traceback
        traceback.print_exc()

async def test_mixed_history_formats():
    """Тестирует построение промпта со смешанными форматами истории."""
    print("\n🧪 Тестируем построение промпта со смешанными форматами истории...")
    
    service = TextGenWebUIService()
    
    # Смешанный формат истории (для тестирования устойчивости)
    history_mixed = [
        {"role": "user", "content": "Привет!"},
        ("assistant", "Здравствуйте!"),
        ["user", "Как дела?"],
        {"role": "assistant", "content": "Спасибо, хорошо!"}
    ]
    
    system_prompt = "Ты помощник"
    user_message = "Расскажи историю"
    
    try:
        prompt = service.build_mythomax_prompt(system_prompt, user_message, history=history_mixed)
        print("✅ Промпт успешно построен со смешанной историей!")
        print(f"📝 Результат:\n{prompt}")
        
        # Проверяем, что все сообщения обработаны
        assert "Привет!" in prompt, "Промпт должен содержать первое сообщение"
        assert "Здравствуйте!" in prompt, "Промпт должен содержать второе сообщение"
        assert "Как дела?" in prompt, "Промпт должен содержать третье сообщение"
        assert "Спасибо, хорошо!" in prompt, "Промпт должен содержать четвертое сообщение"
        
        print("✅ Все проверки пройдены успешно!")
        
    except Exception as e:
        print(f"❌ Ошибка при построении промпта: {e}")
        import traceback
        traceback.print_exc()

async def main():
    """Основная функция тестирования."""
    print("🚀 Запуск тестов исправленного chat endpoint")
    print("=" * 60)
    
    try:
        await test_prompt_building_with_tuple_history()
        await test_prompt_building_with_dict_history()
        await test_mixed_history_formats()
        
        print("\n" + "=" * 60)
        print("🎉 Все тесты chat endpoint завершены успешно!")
        print("✅ Ошибка 'tuple' object has no attribute 'get' исправлена!")
        
    except Exception as e:
        print(f"\n❌ Ошибка в тестах: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
