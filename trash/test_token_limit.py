#!/usr/bin/env python3
"""
Тест ограничения токенов в 250.
Проверяет, что модель действительно соблюдает лимит.
"""

import asyncio
import sys
import os

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.chat_bot.services.textgen_webui_service import TextGenWebUIService
from app.chat_bot.config.chat_config import chat_config

async def test_token_limit():
    """Тестирует ограничение токенов."""
    print("🧪 Тестируем ограничение токенов в 250...")
    print(f"📋 Конфигурация: DEFAULT_MAX_TOKENS = {chat_config.DEFAULT_MAX_TOKENS}")
    print(f"📋 Стоп-токены: {chat_config.DEFAULT_STOP_TOKENS}")
    print()
    
    service = TextGenWebUIService()
    
    try:
        # Проверяем соединение
        if not await service.check_connection():
            print("❌ Не удалось подключиться к text-generation-webui")
            return
            
        print("✅ Подключение к text-generation-webui установлено")
        
        # Тестовый промпт
        test_prompt = "Расскажи подробно о том, как работает машинное обучение и нейронные сети. Объясни все детали, включая различные типы алгоритмов, архитектуры нейросетей, методы обучения и практические применения."
        
        print(f"📝 Тестовый промпт: {len(test_prompt)} символов")
        print()
        
        # Генерируем текст
        print("🚀 Генерируем текст...")
        generated_text = await service.generate_text(test_prompt)
        
        if generated_text:
            # Подсчитываем примерное количество токенов (грубая оценка)
            # В среднем 1 токен ≈ 4 символа для английского, ≈ 3.5 для русского
            estimated_tokens = len(generated_text) // 3.5
            
            print(f"✅ Текст сгенерирован!")
            print(f"📊 Длина ответа: {len(generated_text)} символов")
            print(f"📊 Примерное количество токенов: {estimated_tokens}")
            print(f"🎯 Ограничение: 250 токенов")
            print()
            
            if estimated_tokens <= 250:
                print("✅ Ограничение токенов соблюдается!")
            else:
                print("❌ Ограничение токенов НЕ соблюдается!")
                print(f"   Превышение на {estimated_tokens - 250} токенов")
            
            print()
            print("📄 Сгенерированный текст:")
            print("-" * 50)
            print(generated_text[:500] + "..." if len(generated_text) > 500 else generated_text)
            print("-" * 50)
            
        else:
            print("❌ Не удалось сгенерировать текст")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    finally:
        await service.disconnect()

if __name__ == "__main__":
    asyncio.run(test_token_limit())
