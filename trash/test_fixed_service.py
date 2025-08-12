#!/usr/bin/env python3
"""
Тест исправленного сервиса text-generation-webui.
Проверяет исправление ошибки 'tuple' object has no attribute 'get'.
"""

import asyncio
import sys
import os

# Добавляем путь к проекту
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.chat_bot.services.textgen_webui_service import TextGenWebUIService

async def test_build_prompt():
    """Тестирует метод build_mythomax_prompt с разными форматами истории."""
    print("🧪 Тестируем метод build_mythomax_prompt...")
    
    service = TextGenWebUIService()
    
    # Тест 1: История в формате словарей (правильный формат)
    print("\n📝 Тест 1: История в формате словарей")
    history_dict = [
        {"role": "user", "content": "Привет!"},
        {"role": "assistant", "content": "Здравствуйте!"},
        {"role": "user", "content": "Как дела?"}
    ]
    
    prompt1 = service.build_mythomax_prompt(
        "Ты помощник", 
        "Расскажи анекдот", 
        history=history_dict
    )
    print(f"Результат:\n{prompt1}")
    
    # Тест 2: История в формате кортежей (старый формат)
    print("\n📝 Тест 2: История в формате кортежей")
    history_tuple = [
        ("user", "Привет!"),
        ("assistant", "Здравствуйте!"),
        ("user", "Как дела?")
    ]
    
    prompt2 = service.build_mythomax_prompt(
        "Ты помощник", 
        "Расскажи анекдот", 
        history=history_tuple
    )
    print(f"Результат:\n{prompt2}")
    
    # Тест 3: История в формате списков
    print("\n📝 Тест 3: История в формате списков")
    history_list = [
        ["user", "Привет!"],
        ["assistant", "Здравствуйте!"],
        ["user", "Как дела?"]
    ]
    
    prompt3 = service.build_mythomax_prompt(
        "Ты помощник", 
        "Расскажи анекдот", 
        history=history_list
    )
    print(f"Результат:\n{prompt3}")
    
    # Тест 4: Пустая история
    print("\n📝 Тест 4: Пустая история")
    prompt4 = service.build_mythomax_prompt(
        "Ты помощник", 
        "Расскажи анекдот", 
        history=[]
    )
    print(f"Результат:\n{prompt4}")
    
    # Тест 5: Некорректная история
    print("\n📝 Тест 5: Некорректная история")
    history_bad = [
        "просто строка",
        {"role": "user", "content": "Привет!"},
        None,
        {"role": "assistant", "content": "Здравствуйте!"}
    ]
    
    prompt5 = service.build_mythomax_prompt(
        "Ты помощник", 
        "Расскажи анекдот", 
        history=history_bad
    )
    print(f"Результат:\n{prompt5}")
    
    print("\n✅ Все тесты build_mythomax_prompt завершены!")

async def test_service_initialization():
    """Тестирует инициализацию сервиса."""
    print("\n🧪 Тестируем инициализацию сервиса...")
    
    try:
        service = TextGenWebUIService()
        print(f"✅ Сервис создан успешно")
        print(f"   Base URL: {service.base_url}")
        print(f"   Model: {service.model_name}")
        print(f"   Timeout: {service.timeout}")
        print(f"   Is connected: {service.is_connected}")
        print(f"   Is available: {service.is_available}")
        
    except Exception as e:
        print(f"❌ Ошибка при создании сервиса: {e}")

async def main():
    """Основная функция тестирования."""
    print("🚀 Запуск тестов исправленного сервиса text-generation-webui")
    print("=" * 60)
    
    try:
        await test_service_initialization()
        await test_build_prompt()
        
        print("\n" + "=" * 60)
        print("🎉 Все тесты завершены успешно!")
        
    except Exception as e:
        print(f"\n❌ Ошибка в тестах: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
