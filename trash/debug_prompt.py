#!/usr/bin/env python3
"""
Диагностика формирования промпта для Anna.
Показывает, как именно формируется финальный промпт.
"""

import sys
import os

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.chat_bot.models.characters.anna import (
    get_instructions, 
    get_system_prompt, 
    get_response_format,
    get_mythomax_prompt_with_user_message
)

def debug_prompt():
    """Анализирует формирование промпта."""
    print("🔍 ДИАГНОСТИКА ПРОМПТА ANNA")
    print("=" * 60)
    
    # Получаем компоненты
    instructions = get_instructions()
    system_prompt = get_system_prompt()
    response_format = get_response_format()
    
    print("\n📋 SYSTEM PROMPT:")
    print("-" * 30)
    print(system_prompt)
    
    print("\n📋 INSTRUCTIONS:")
    print("-" * 30)
    print(instructions)
    
    print("\n📋 RESPONSE FORMAT:")
    print("-" * 30)
    print(response_format)
    
    print("\n📋 ПОЛНЫЙ ПРОМПТ MYTHOMAX:")
    print("-" * 30)
    test_message = "Come here, Anna. I want to hold you close to me."
    full_prompt = get_mythomax_prompt_with_user_message(test_message)
    print(full_prompt)
    
    print("\n📊 СТАТИСТИКА:")
    print("-" * 30)
    print(f"System prompt: {len(system_prompt)} символов")
    print(f"Instructions: {len(instructions)} символов")
    print(f"Response format: {len(response_format)} символов")
    print(f"Full prompt: {len(full_prompt)} символов")
    
    # Проверяем ключевые элементы
    print("\n🔍 ПРОВЕРКА КЛЮЧЕВЫХ ЭЛЕМЕНТОВ:")
    print("-" * 30)
    
    if "CRITICAL QUESTION RULES" in instructions:
        print("✅ CRITICAL QUESTION RULES найдены")
    else:
        print("❌ CRITICAL QUESTION RULES НЕ найдены")
    
    if "ALWAYS end with a direct question" in instructions:
        print("✅ Инструкция о завершении вопросом найдена")
    else:
        print("❌ Инструкция о завершении вопросом НЕ найдена")
    
    if "you" in instructions.lower() and "your" in instructions.lower():
        print("✅ Местоимения 'you', 'your' найдены")
    else:
        print("❌ Местоимения 'you', 'your' НЕ найдены")
    
    if "NEVER ask: 'What if I...'" in instructions:
        print("✅ Запрет на неправильные вопросы найден")
    else:
        print("❌ Запрет на неправильные вопросы НЕ найден")

if __name__ == "__main__":
    debug_prompt()
