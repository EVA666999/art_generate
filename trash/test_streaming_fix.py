#!/usr/bin/env python3
"""
Тест для проверки исправления streaming функциональности
"""

import asyncio
import sys
import os

# Добавляем путь к проекту
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.chat_bot.services.textgen_webui_service import TextGenWebUIService

async def test_generate_stream_method():
    """Тестируем метод generate_stream как алиас для generate_text_stream"""
    print("🧪 Тестируем метод generate_stream...")
    
    service = TextGenWebUIService()
    
    # Проверяем, что метод существует
    if hasattr(service, 'generate_stream'):
        print("✅ Метод generate_stream найден")
    else:
        print("❌ Метод generate_stream НЕ найден")
        return False
    
    # Проверяем, что это алиас для generate_text_stream
    if hasattr(service, 'generate_text_stream'):
        print("✅ Метод generate_text_stream найден")
    else:
        print("❌ Метод generate_text_stream НЕ найден")
        return False
    
    # Проверяем сигнатуры методов
    import inspect
    
    stream_sig = inspect.signature(service.generate_stream)
    text_stream_sig = inspect.signature(service.generate_text_stream)
    
    print(f"📝 Сигнатура generate_stream: {stream_sig}")
    print(f"📝 Сигнатура generate_text_stream: {text_stream_sig}")
    
    # Проверяем, что параметры совпадают
    stream_params = list(stream_sig.parameters.keys())
    text_stream_params = list(text_stream_sig.parameters.keys())
    
    # Убираем 'self' из параметров
    stream_params = [p for p in stream_params if p != 'self']
    text_stream_params = [p for p in text_stream_params if p != 'self']
    
    if stream_params == text_stream_params:
        print("✅ Параметры методов совпадают")
    else:
        print(f"❌ Параметры методов НЕ совпадают:")
        print(f"   generate_stream: {stream_params}")
        print(f"   generate_text_stream: {text_stream_params}")
        return False
    
    return True

async def test_parameter_names():
    """Тестируем правильность имен параметров"""
    print("\n🧪 Тестируем имена параметров...")
    
    # Проверяем, что используется max_tokens, а не max_new_tokens
    service = TextGenWebUIService()
    
    # Получаем сигнатуру метода
    import inspect
    sig = inspect.signature(service.generate_text_stream)
    
    # Проверяем, что есть параметр max_tokens
    if 'max_tokens' in sig.parameters:
        print("✅ Параметр max_tokens найден")
    else:
        print("❌ Параметр max_tokens НЕ найден")
        return False
    
    # Проверяем, что НЕТ параметра max_new_tokens
    if 'max_new_tokens' not in sig.parameters:
        print("✅ Параметр max_new_tokens НЕ найден (как и должно быть)")
    else:
        print("❌ Параметр max_new_tokens найден (не должно быть)")
        return False
    
    return True

async def main():
    """Основная функция тестирования"""
    print("🚀 Запуск тестов streaming функциональности...\n")
    
    # Тест 1: Проверка метода generate_stream
    test1_passed = await test_generate_stream_method()
    
    # Тест 2: Проверка имен параметров
    test2_passed = await test_parameter_names()
    
    print("\n" + "="*50)
    if test1_passed and test2_passed:
        print("🎉 ВСЕ ТЕСТЫ ПРОШЛИ УСПЕШНО!")
        print("✅ Streaming функциональность исправлена")
    else:
        print("❌ НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОШЛИ")
        print("🔧 Требуется дополнительная отладка")
    
    print("="*50)

if __name__ == "__main__":
    asyncio.run(main())
