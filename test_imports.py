#!/usr/bin/env python3
"""
Тестовый скрипт для проверки импортов
"""
import sys
import os

# Добавляем путь к app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_imports():
    """Тестирует импорты"""
    print("🔍 Тестирование импортов...")
    
    try:
        print("1. Тестируем chat_endpoints...")
        from chat_bot.api.chat_endpoints import router as chat_router
        print("   ✅ chat_endpoints импортирован успешно")
        print(f"   📍 Префикс: {chat_router.prefix}")
        print(f"   🏷️ Теги: {chat_router.tags}")
        
        # Проверяем routes
        routes = [route.path for route in chat_router.routes]
        print(f"   🛣️ Маршруты: {routes}")
        
    except Exception as e:
        print(f"   ❌ Ошибка импорта chat_endpoints: {e}")
        import traceback
        traceback.print_exc()
    
    try:
        print("\n2. Тестируем character_endpoints...")
        from chat_bot.api.character_endpoints import router as character_router
        print("   ✅ character_endpoints импортирован успешно")
        print(f"   📍 Префикс: {character_router.prefix}")
        print(f"   🏷️ Теги: {character_router.tags}")
        
        # Проверяем routes
        routes = [route.path for route in character_router.routes]
        print(f"   🛣️ Маршруты: {routes}")
        
    except Exception as e:
        print(f"   ❌ Ошибка импорта character_endpoints: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_imports() 