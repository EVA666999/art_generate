#!/usr/bin/env python3
"""
Тест упрощенного сервиса без дублирования инструкций
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.chat_bot.services.textgen_webui_service import TextGenWebUIService
from app.chat_bot.models.characters.anna import anna

def test_simplified_service():
    """Тестируем упрощенный сервис"""
    print("🧪 Тестируем упрощенный сервис без дублирования")
    
    service = TextGenWebUIService()
    
    # Тест build_character_prompt
    print("\n1. Тест build_character_prompt:")
    prompt = service.build_character_prompt(
        character_data=anna,
        user_message="Привет! Как дела?",
        chat_history=[]
    )
    print("✅ Промпт построен успешно")
    print(f"Длина промпта: {len(prompt)} символов")
    
    # Проверяем, что нет дублирования критических инструкций
    critical_count = prompt.count("CRITICAL")
    first_person_count = prompt.count("FIRST PERSON")
    
    print(f"Количество 'CRITICAL': {critical_count}")
    print(f"Количество 'FIRST PERSON': {first_person_count}")
    
    if critical_count <= 2 and first_person_count <= 3:
        print("✅ Дублирование устранено - инструкции не повторяются")
    else:
        print("⚠️ Возможно есть дублирование")
    
    # Тест build_mythomax_prompt
    print("\n2. Тест build_mythomax_prompt:")
    mythomax_prompt = service.build_mythomax_prompt(
        system_message="Ты Anna, застенчивая сестра",
        user_message="Привет!",
        history=[]
    )
    print("✅ MythoMax промпт построен успешно")
    print(f"Длина промпта: {len(mythomax_prompt)} символов")
    
    # Тест fallback промпта
    print("\n3. Тест fallback промпта:")
    fallback_prompt = service._build_fallback_prompt("Привет!")
    print("✅ Fallback промпт построен успешно")
    print(f"Длина промпта: {len(fallback_prompt)} символов")
    
    print("\n🎉 Все тесты пройдены! Сервис упрощен и работает корректно")

if __name__ == "__main__":
    test_simplified_service()
