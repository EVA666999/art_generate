#!/usr/bin/env python3
"""
Тест интеграции с text-generation-webui.
Проверяет подключение, загрузку модели и генерацию текста.
"""

import asyncio
import sys
import os
from pathlib import Path

# Добавляем корневую директорию проекта в PYTHONPATH
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.services.textgen_webui_service import TextGenWebUIService
from app.chat_bot.models.characters.anna import get_character_data


async def test_textgen_webui_connection():
    """Тест подключения к text-generation-webui."""
    print("🔌 Тестируем подключение к text-generation-webui...")
    
    service = TextGenWebUIService()
    
    try:
        # Проверяем доступность
        is_available = await service.check_availability()
        print(f"✅ Доступность: {is_available}")
        
        if is_available:
            # Получаем информацию о модели
            model_info = await service.get_model_info()
            print(f"📊 Информация о модели: {model_info}")
            
            # Получаем список доступных моделей
            models = await service.get_available_models()
            print(f"📚 Доступные модели: {models}")
            
            # Проверяем здоровье сервиса
            health = await service.health_check()
            print(f"🏥 Статус здоровья: {health}")
            
        return is_available
        
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        return False
    finally:
        await service.close_session()


async def test_text_generation():
    """Тест генерации текста."""
    print("\n🚀 Тестируем генерацию текста...")
    
    service = TextGenWebUIService()
    
    try:
        # Проверяем доступность
        is_available = await service.check_availability()
        if not is_available:
            print("⚠️ Сервер недоступен, пропускаем тест генерации")
            return False
            
        # Простой тест генерации
        test_prompt = "Привет! Как дела?"
        print(f"📝 Тестовый промпт: {test_prompt}")
        
        print("⏳ Генерируем текст...")
        response = await service.generate_text(test_prompt)
        print(f"✅ Ответ получен ({len(response)} символов):")
        print(f"📄 {response[:200]}{'...' if len(response) > 200 else ''}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка генерации: {e}")
        return False
    finally:
        await service.close_session()


async def test_mythomax_character_response():
    """Тест генерации ответа персонажа в формате MythoMax."""
    print("\n🎭 Тестируем генерацию ответа персонажа Anna...")
    
    service = TextGenWebUIService()
    
    try:
        # Проверяем доступность
        is_available = await service.check_availability()
        if not is_available:
            print("⚠️ Сервер недоступен, пропускаем тест персонажа")
            return False
            
        # Получаем данные персонажа Anna
        character_data = get_character_data()
        user_message = "Привет, как ты себя чувствуешь?"
        
        print(f"👤 Персонаж: {character_data['name']}")
        print(f"💬 Сообщение пользователя: {user_message}")
        
        print("⏳ Генерируем ответ персонажа...")
        response = await service.generate_mythomax_response(
            character_data=character_data,
            user_message=user_message
        )
        
        print(f"✅ Ответ персонажа получен ({len(response)} символов):")
        print(f"🎭 {response}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка генерации персонажа: {e}")
        return False
    finally:
        await service.close_session()


async def test_streaming_generation():
    """Тест потоковой генерации текста."""
    print("\n🌊 Тестируем потоковую генерацию...")
    
    service = TextGenWebUIService()
    
    try:
        # Проверяем доступность
        is_available = await service.check_availability()
        if not is_available:
            print("⚠️ Сервер недоступен, пропускаем тест стриминга")
            return False
            
        # Тест потоковой генерации
        test_prompt = "Расскажи короткую историю о коте."
        print(f"📝 Тестовый промпт: {test_prompt}")
        
        print("⏳ Генерируем потоковый текст...")
        full_response = ""
        chunk_count = 0
        
        async for chunk in service.generate_text_stream(test_prompt):
            full_response += chunk
            chunk_count += 1
            print(f"📦 Чанк {chunk_count}: {chunk[:50]}{'...' if len(chunk) > 50 else ''}")
            
        print(f"✅ Потоковая генерация завершена:")
        print(f"📊 Всего чанков: {chunk_count}")
        print(f"📄 Полный ответ ({len(full_response)} символов):")
        print(f"📖 {full_response[:300]}{'...' if len(full_response) > 300 else ''}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка потоковой генерации: {e}")
        return False
    finally:
        await service.close_session()


async def main():
    """Основная функция тестирования."""
    print("🧪 Запуск тестов интеграции с text-generation-webui")
    print("=" * 60)
    
    # Тест 1: Подключение
    connection_ok = await test_textgen_webui_connection()
    
    if connection_ok:
        # Тест 2: Генерация текста
        generation_ok = await test_text_generation()
        
        # Тест 3: Ответ персонажа
        character_ok = await test_mythomax_character_response()
        
        # Тест 4: Потоковая генерация
        streaming_ok = await test_streaming_generation()
        
        # Итоговый отчет
        print("\n" + "=" * 60)
        print("📊 ИТОГОВЫЙ ОТЧЕТ:")
        print(f"🔌 Подключение: {'✅' if connection_ok else '❌'}")
        print(f"🚀 Генерация текста: {'✅' if generation_ok else '❌'}")
        print(f"🎭 Ответ персонажа: {'✅' if character_ok else '❌'}")
        print(f"🌊 Потоковая генерация: {'✅' if streaming_ok else '❌'}")
        
        success_count = sum([connection_ok, generation_ok, character_ok, streaming_ok])
        total_tests = 4
        
        print(f"\n🎯 Результат: {success_count}/{total_tests} тестов прошли успешно")
        
        if success_count == total_tests:
            print("🎉 Все тесты прошли успешно! Интеграция работает корректно.")
        else:
            print("⚠️ Некоторые тесты не прошли. Проверьте настройки и логи.")
            
    else:
        print("\n❌ Не удалось подключиться к text-generation-webui")
        print("💡 Убедитесь, что:")
        print("   1. text-generation-webui запущен на http://127.0.0.1:5000")
        print("   2. Модель Gryphe-MythoMax-L2-13b.Q4_K_S.gguf загружена")
        print("   3. API включен в настройках WebUI")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️ Тестирование прервано пользователем")
    except Exception as e:
        print(f"\n💥 Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
