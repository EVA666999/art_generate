#!/usr/bin/env python3
"""
Тест качества вопросов персонажа Anna.
Проверяет, что модель задает прямые вопросы к пользователю.
"""

import asyncio
import sys
import os

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.chat_bot.services.textgen_webui_service import TextGenWebUIService
from app.chat_bot.models.characters.anna import get_mythomax_prompt_with_user_message

async def test_anna_questions():
    """Тестирует качество вопросов Anna."""
    print("🧪 Тестируем качество вопросов Anna...")
    print("🎯 Цель: Anna должна задавать прямые вопросы к пользователю")
    print()

    service = TextGenWebUIService()

    try:
        # Проверяем соединение
        if not await service.check_connection():
            print("❌ Не удалось подключиться к text-generation-webui")
            return

        print("✅ Подключение к text-generation-webui установлено")

        # Тестовый промпт - от имени брата к Anna
        test_prompt = "Come here, Anna. I want to hold you close to me."

        print(f"📝 Тестовый промпт: {test_prompt}")
        print()

        # Создаем промпт в формате MythoMax
        full_prompt = get_mythomax_prompt_with_user_message(test_prompt)
        
        print("🚀 Генерируем ответ Anna...")
        generated_text = await service.generate_text(full_prompt)

        if generated_text:
            print(f"✅ Ответ сгенерирован!")
            print(f"📊 Длина ответа: {len(generated_text)} символов")
            print()
            
            # Анализируем качество вопроса
            print("🔍 Анализируем качество вопроса...")
            
            # Проверяем, заканчивается ли ответ вопросом
            if generated_text.strip().endswith('?'):
                print("✅ Ответ заканчивается вопросом")
            else:
                print("❌ Ответ НЕ заканчивается вопросом")
            
            # Проверяем, содержит ли вопрос местоимения "you", "your"
            if 'you' in generated_text.lower() or 'your' in generated_text.lower():
                print("✅ Вопрос обращен к пользователю (содержит 'you', 'your')")
            else:
                print("❌ Вопрос НЕ обращен к пользователю (нет 'you', 'your')")
            
            # Проверяем на риторические вопросы
            rhetorical_indicators = [
                'what does this mean', 'i wonder', 'do we continue', 
                'what will happen', 'i think', 'maybe'
            ]
            
            has_rhetorical = any(indicator in generated_text.lower() for indicator in rhetorical_indicators)
            if not has_rhetorical:
                print("✅ Нет риторических вопросов")
            else:
                print("⚠️  Обнаружены риторические элементы")
            
            print()
            print("📄 Сгенерированный ответ:")
            print("-" * 50)
            print(generated_text)
            print("-" * 50)
            
            # Итоговая оценка
            print()
            print("📊 ИТОГОВАЯ ОЦЕНКА:")
            if (generated_text.strip().endswith('?') and 
                ('you' in generated_text.lower() or 'your' in generated_text.lower()) and
                not has_rhetorical):
                print("🎉 ОТЛИЧНО! Anna задает правильный прямой вопрос к пользователю!")
            elif generated_text.strip().endswith('?'):
                print("👍 Хорошо: есть вопрос, но может быть улучшен")
            else:
                print("❌ Требует доработки: нет прямого вопроса к пользователю")

        else:
            print("❌ Не удалось сгенерировать ответ")

    except Exception as e:
        print(f"❌ Ошибка: {e}")
    finally:
        await service.disconnect()

if __name__ == "__main__":
    asyncio.run(test_anna_questions())
