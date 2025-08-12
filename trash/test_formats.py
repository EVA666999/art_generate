#!/usr/bin/env python3
"""
Тест правильности форматов для MythoMax L2 13B
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'app'))

from services.textgen_webui_service import TextGenWebUIService, DEFAULT_MYTHOMAX_PARAMS

def test_prompt_format():
    """Тестируем правильность формата промпта"""
    print("🔧 Тестирование формата промпта для MythoMax L2 13B")
    print("=" * 60)
    
    # Создаем тестовые данные персонажа
    character_data = {
        "name": "Anna",
        "instructions": "Ты Анна - дружелюбная и заботливая девушка. Всегда отвечай от первого лица.",
        "system_prompt": "Ты персонаж по имени Анна. Веди себя естественно и дружелюбно.",
        "response_format": "Отвечай кратко и по-дружески, используя 'я' и 'меня'."
    }
    
    # Создаем тестовую историю разговора
    conversation_history = [
        {"role": "user", "content": "Привет! Как дела?"},
        {"role": "assistant", "content": "Привет! У меня все хорошо, спасибо что спросил!"},
        {"role": "user", "content": "Что ты сегодня делала?"}
    ]
    
    user_message = "Расскажи о своем дне"
    
    # Создаем сервис и строим промпт
    service = TextGenWebUIService()
    prompt = service._build_mythomax_prompt(
        character_data=character_data,
        user_message=user_message,
        conversation_history=conversation_history
    )
    
    print("📝 Сформированный промпт:")
    print("-" * 40)
    print(prompt)
    print("-" * 40)
    
    # Проверяем наличие ключевых элементов
    checks = [
        ("### Instruction:", "Инструкции персонажа"),
        ("### Human:", "Сообщения пользователя"),
        ("### Assistant:", "Ответы ассистента"),
        ("Ты Anna", "Имя персонажа"),
        ("Привет! Как дела?", "История разговора"),
        ("Расскажи о своем дне", "Текущее сообщение")
    ]
    
    print("\n✅ Проверка элементов промпта:")
    for check_text, description in checks:
        if check_text in prompt:
            print(f"   ✅ {description}: найдено")
        else:
            print(f"   ❌ {description}: НЕ найдено")
    
    return prompt

def test_parameters():
    """Тестируем правильность параметров"""
    print("\n🔧 Тестирование параметров MythoMax L2 13B")
    print("=" * 60)
    
    print("📊 Текущие параметры:")
    for param, value in DEFAULT_MYTHOMAX_PARAMS.items():
        print(f"   {param}: {value}")
    
    # Проверяем ключевые параметры
    required_params = {
        "temperature": (0.7, 0.9),      # Оптимальный диапазон для ролевых игр
        "top_p": (0.8, 0.95),          # Оптимальный диапазон
        "typical_p": (0.9, 0.98),      # Новый параметр MythoMax
        "mirostat": (1, 3),            # Должен быть включен
        "stop": list                    # Должен быть список
    }
    
    print("\n✅ Проверка параметров:")
    for param, expected in required_params.items():
        if param in DEFAULT_MYTHOMAX_PARAMS:
            value = DEFAULT_MYTHOMAX_PARAMS[param]
            if isinstance(expected, tuple):
                if expected[0] <= value <= expected[1]:
                    print(f"   ✅ {param}: {value} (в диапазоне {expected})")
                else:
                    print(f"   ⚠️ {param}: {value} (вне диапазона {expected})")
            elif isinstance(expected, type):
                if isinstance(value, expected):
                    print(f"   ✅ {param}: {value} (правильный тип)")
                else:
                    print(f"   ❌ {param}: {value} (неправильный тип)")
        else:
            print(f"   ❌ {param}: отсутствует")

def test_response_cleaning():
    """Тестируем очистку ответов"""
    print("\n🔧 Тестирование очистки ответов")
    print("=" * 60)
    
    service = TextGenWebUIService()
    
    test_responses = [
        "### Assistant: Привет! Как дела?",
        "### Human: Привет! ### Assistant: У меня все хорошо!",
        "### Instruction: Будь дружелюбной ### Assistant: Конечно!",
        "Assistant: Я рада тебя видеть!",
        "### Response: Все отлично! ### Output: Замечательно!"
    ]
    
    print("🧹 Тестирование очистки:")
    for response in test_responses:
        cleaned = service._clean_mythomax_response(response)
        print(f"   До: {response}")
        print(f"   После: {cleaned}")
        print()

if __name__ == "__main__":
    print("🚀 Тест форматов MythoMax L2 13B")
    print("=" * 60)
    
    try:
        # Тестируем формат промпта
        prompt = test_prompt_format()
        
        # Тестируем параметры
        test_parameters()
        
        # Тестируем очистку ответов
        test_response_cleaning()
        
        print("\n🎉 Все тесты завершены!")
        
    except Exception as e:
        print(f"\n❌ Ошибка при тестировании: {e}")
        import traceback
        traceback.print_exc()
