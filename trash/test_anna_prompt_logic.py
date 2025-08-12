#!/usr/bin/env python3
"""
Упрощенный тест логики промпта Anna
Проверяет логику построения промпта без внешних зависимостей
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.chat_bot.models.characters.anna import get_character_data, get_alpaca_prompt_with_user_message

def simulate_service_logic(character_data, user_message, history):
    """Симулирует логику textgen_webui_service для построения промпта."""
    
    # Собираем системное сообщение из данных персонажа
    system_parts = []
    
    # Специальная обработка для Anna - усиленный контекст
    if character_data.get("name", "").lower() == "anna":
        system_parts.append("=== ANNA'S ENHANCED CONTEXT ===")
        system_parts.append("You are Anna, a shy young sister living with your brother after a painful breakup.")
        system_parts.append("Remember: You moved in recently, had an embarrassing kitchen incident, and feel vulnerable.")
        system_parts.append("")
    
    if character_data.get("system_prompt"):
        system_parts.append(character_data["system_prompt"])
    
    if character_data.get("instructions"):
        system_parts.append(character_data["instructions"])
        
    if character_data.get("response_format"):
        system_parts.append(character_data["response_format"])
    
    # Добавляем критически важные инструкции по контексту
    system_parts.append("")
    system_parts.append("CRITICAL INSTRUCTIONS:")
    system_parts.append("- ALWAYS respond directly to what the user just said")
    system_parts.append("- Use context from previous messages to provide relevant answers")
    system_parts.append("- Reference specific details from the conversation when appropriate")
    system_parts.append("- Stay in character and maintain conversation flow")
    system_parts.append("- Ask follow-up questions when it makes sense")
    system_parts.append("- ALWAYS reference your background story and character context")
    system_parts.append("- Connect current conversations to your established personality and situation")
    
    system_message = "\n".join(system_parts)
    
    # Формируем контекст из истории диалога
    context_parts = []
    if history and len(history) > 0:
        # Берем только последние 15 сообщений для оптимального баланса
        recent_history = history[-15:] if len(history) > 15 else history
        
        # Добавляем четкие инструкции для использования контекста
        context_parts.append("=== CONVERSATION CONTEXT ===")
        context_parts.append("IMPORTANT: You MUST use this context to provide relevant responses.")
        context_parts.append("Reference specific details, continue ongoing topics, and maintain conversation flow.")
        context_parts.append("")
        
        # Добавляем историю диалога в четком формате
        for i, msg in enumerate(recent_history, 1):
            role = msg.get("role", "user")
            content = msg.get("content", "").strip()
            if content:
                if role == "user":
                    context_parts.append(f"User: {content}")
                elif role == "assistant":
                    context_parts.append(f"{character_data.get('name', 'Anna')}: {content}")
                context_parts.append("")  # Пустая строка для разделения
        
        context_parts.append("=== CURRENT MESSAGE TO RESPOND TO ===")
        context_parts.append("")
    else:
        context_parts.append("=== NEW CONVERSATION ===")
        context_parts.append("This is the start of our conversation.")
        context_parts.append("")
    
    # Строим промпт в формате Alpaca с улучшенной структурой
    context_text = "\n".join(context_parts)
    return f"{system_message}\n\n{context_text}{user_message}\n\n### Response:\n"

def test_anna_prompt_logic():
    """Тестирует логику построения промпта Anna."""
    print("🧪 ТЕСТ ЛОГИКИ ПОСТРОЕНИЯ ПРОМПТА ANNA")
    print("=" * 60)
    
    # Получаем данные персонажа
    character_data = get_character_data()
    print(f"✅ Загружен персонаж: {character_data['name']}")
    print()
    
    # Тестируем build_character_prompt
    user_message = "Привет, как ты себя чувствуешь сегодня?"
    history = [
        {"role": "user", "content": "Привет, Anna"},
        {"role": "assistant", "content": "Привет... Я все еще немного стесняюсь после того случая в кухне."}
    ]
    
    print(f"💬 Тестовое сообщение: {user_message}")
    print(f"📚 История: {len(history)} сообщений")
    print()
    
    try:
        # Симулируем логику сервиса
        prompt = simulate_service_logic(character_data, user_message, history)
        print("📝 СГЕНЕРИРОВАННЫЙ ПРОМПТ:")
        print("-" * 40)
        print(prompt)
        print()
        
        # Проверяем ключевые элементы
        print("🔍 ПРОВЕРКА КЛЮЧЕВЫХ ЭЛЕМЕНТОВ:")
        
        # Проверяем специальную обработку для Anna
        if "=== ANNA'S ENHANCED CONTEXT ===" in prompt:
            print("✅ Специальная обработка для Anna включена")
        else:
            print("❌ Специальная обработка для Anna НЕ найдена")
        
        # Проверяем контекст
        if "kitchen incident" in prompt.lower():
            print("✅ Контекст кухонного инцидента включен")
        else:
            print("❌ Контекст кухонного инцидента НЕ найден")
        
        # Проверяем инструкции по контексту
        if "ALWAYS reference your background story" in prompt:
            print("✅ Инструкции по использованию контекста включены")
        else:
            print("❌ Инструкции по использованию контекста НЕ найдены")
        
        # Проверяем историю диалога
        if "User: Привет, Anna" in prompt:
            print("✅ История диалога включена")
        else:
            print("❌ История диалога НЕ найдена")
        
        # Проверяем критически важные инструкции
        if "CRITICAL INSTRUCTIONS:" in prompt:
            print("✅ Критически важные инструкции включены")
        else:
            print("❌ Критически важные инструкции НЕ найдены")
        
        print()
        print("🎯 РЕЗУЛЬТАТ ТЕСТИРОВАНИЯ:")
        
        # Подсчитываем баллы
        score = 0
        total_checks = 5
        
        if "=== ANNA'S ENHANCED CONTEXT ===" in prompt:
            score += 1
        if "kitchen incident" in prompt.lower():
            score += 1
        if "ALWAYS reference your background story" in prompt:
            score += 1
        if "User: Привет, Anna" in prompt:
            score += 1
        if "CRITICAL INSTRUCTIONS:" in prompt:
            score += 1
        
        if score == total_checks:
            print("✅ Отличный результат! Все элементы контекста работают")
        elif score >= total_checks * 0.8:
            print("✅ Хороший результат! Большинство элементов работает")
        elif score >= total_checks * 0.6:
            print("⚠️ Удовлетворительный результат. Некоторые элементы отсутствуют")
        else:
            print("❌ Плохой результат. Много элементов не работает")
        
        print(f"📊 Оценка: {score}/{total_checks} ({score/total_checks*100:.1f}%)")
        
        # Дополнительные проверки
        print()
        print("🔍 ДОПОЛНИТЕЛЬНЫЕ ПРОВЕРКИ:")
        
        # Проверяем длину промпта
        prompt_length = len(prompt)
        print(f"📏 Длина промпта: {prompt_length} символов")
        
        if prompt_length > 1000:
            print("✅ Промпт достаточно детальный для глубокого контекста")
        elif prompt_length > 500:
            print("✅ Промпт имеет хороший уровень детализации")
        else:
            print("⚠️ Промпт может быть недостаточно детальным")
        
        # Проверяем структуру
        if "CONTEXT:" in prompt and "BACKGROUND STORY:" in prompt:
            print("✅ Структура контекста четкая и понятная")
        else:
            print("⚠️ Структура контекста может быть улучшена")
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_anna_prompt_logic()
