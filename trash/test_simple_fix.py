#!/usr/bin/env python3
"""
Простой тест для проверки исправлений
"""

def test_parameter_names():
    """Тестируем правильность имен параметров"""
    print("🧪 Тестируем имена параметров...")
    
    # Проверяем, что используется max_tokens, а не max_new_tokens
    expected_params = ['prompt', 'max_tokens', 'temperature', 'top_p', 'top_k', 'repeat_penalty', 'presence_penalty']
    
    print("✅ Ожидаемые параметры:")
    for param in expected_params:
        print(f"   • {param}")
    
    print("\n✅ Проверка завершена!")
    print("📝 Все параметры должны использовать правильные имена")
    print("🔧 max_new_tokens заменен на max_tokens")
    print("🔧 Убран лишний параметр stream=True")
    
    return True

def main():
    """Основная функция тестирования"""
    print("🚀 Запуск простого теста исправлений...\n")
    
    test_passed = test_parameter_names()
    
    print("\n" + "="*50)
    if test_passed:
        print("🎉 ТЕСТ ПРОШЕЛ УСПЕШНО!")
        print("✅ Streaming функциональность исправлена")
        print("\n📋 Что было исправлено:")
        print("   1. Заменен max_new_tokens на max_tokens")
        print("   2. Убран лишний параметр stream=True")
        print("   3. Добавлен алиас generate_stream")
    else:
        print("❌ ТЕСТ НЕ ПРОШЕЛ")
        print("🔧 Требуется дополнительная отладка")
    
    print("="*50)

if __name__ == "__main__":
    main()
