#!/usr/bin/env python3
"""
Тест контекстной памяти для персонажа Anna.
Проверяет, что модель помнит предыдущие 20 сообщений.
"""

import asyncio
import sys
import os

# Добавляем путь к проекту
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.chat_bot.services.textgen_webui_service import TextGenWebUIService
from app.chat_bot.models.characters.anna import CHARACTER_DATA

async def test_context_memory():
    """Тестируем контекстную память на 20 сообщений."""
    print("🧪 Тестируем контекстную память на 20 сообщений...")
    
    # Создаем сервис
    service = TextGenWebUIService()
    
    try:
        # Подключаемся к text-generation-webui
        await service.connect()
        
        # Проверяем соединение
        if not await service.check_connection():
            print("❌ Не удалось подключиться к text-generation-webui")
            return
        
        print("✅ Подключение к text-generation-webui установлено")
        
        # Создаем историю из 20 сообщений с разными темами
        history = []
        
        # Сообщения пользователя (10 штук) - только на английском
        user_messages = [
            "Hello! My name is Michael.",
            "I work as a programmer in an IT company.",
            "My main programming language is Python.",
            "I create web applications using Django and FastAPI.",
            "I also work with databases like PostgreSQL and MongoDB.",
            "I have experience in machine learning and AI.",
            "I use libraries like scikit-learn and TensorFlow.",
            "I'm currently studying microservices architecture.",
            "I work with Docker and Kubernetes for deployment.",
            "My favorite code editor is VS Code."
        ]
        
        # Ответы Anna (10 штук) - только на английском
        anna_responses = [
            "Hello, Michael! Nice to meet you!",
            "Oh, a programmer! That's so interesting!",
            "Python is an excellent choice! I've heard it's very popular.",
            "Django and FastAPI are modern frameworks, right?",
            "Databases are the foundation of any application.",
            "Machine learning sounds exciting!",
            "scikit-learn and TensorFlow are powerful tools.",
            "Microservices is a complex but interesting topic.",
            "Docker and Kubernetes are for containerization, right?",
            "VS Code is an excellent editor! I've heard many good things about it."
        ]
        
        # Формируем историю диалога
        for i in range(10):
            history.append({"role": "user", "content": user_messages[i]})
            history.append({"role": "assistant", "content": anna_responses[i]})
        
        print(f"📝 Создана история из {len(history)} сообщений")
        
        # Тест 1: Промпт БЕЗ истории
        print("\n📝 Тест 1: Промпт БЕЗ истории")
        prompt_without_history = service.build_character_prompt(
            CHARACTER_DATA, 
            "Расскажи о себе", 
            history=None
        )
        print(f"Длина промпта: {len(prompt_without_history)} символов")
        
        # Тест 2: Промпт С историей (20 сообщений)
        print("\n📝 Тест 2: Промпт С историей (20 сообщений)")
        prompt_with_history = service.build_character_prompt(
            CHARACTER_DATA, 
            "What do you remember about our conversation?", 
            history=history
        )
        print(f"Длина промпта с историей: {len(prompt_with_history)} символов")
        
        # Показываем последнюю часть промпта, где должна быть история
        print("Последние 1000 символов промпта (где должна быть история):")
        print(prompt_with_history[-1000:])
        
        # Тест 3: Генерируем ответ с контекстом
        print("\n🤖 Тест 3: Генерируем ответ с контекстом")
        print("Генерируем ответ на основе истории...")
        
        async for chunk in service.generate_text_stream(
            prompt_with_history,
            max_tokens=200,
            temperature=0.7
        ):
            print(chunk, end="", flush=True)
        
        print("\n\n📊 Анализ ответа:")
        
        # Проверяем, упоминает ли модель ключевые детали из истории
        response_text = ""
        async for chunk in service.generate_text_stream(
            prompt_with_history,
            max_tokens=200,
            temperature=0.7
        ):
            response_text += chunk
        
        print(f"Полный ответ: {response_text}")
        
        # Проверяем ключевые слова из контекста
        context_keywords = [
            "Michael", "programmer", "Python", "Django", "FastAPI", 
            "PostgreSQL", "MongoDB", "machine learning", "AI", "Docker", 
            "Kubernetes", "VS Code", "scikit-learn", "TensorFlow",
            "microservices", "frameworks", "databases", "deployment"
        ]
        
        found_keywords = []
        for keyword in context_keywords:
            if keyword.lower() in response_text.lower():
                found_keywords.append(keyword)
        
        print(f"Найдены ключевые слова из контекста: {found_keywords}")
        
        if len(found_keywords) >= 3:
            print("✅ Модель ХОРОШО помнит контекст диалога!")
        elif len(found_keywords) >= 1:
            print("⚠️ Модель частично помнит контекст")
        else:
            print("❌ Модель НЕ помнит контекст диалога")
        
        # Проверяем конкретные детали
        print("\n🔍 Детальный анализ ответа:")
        
        if "michael" in response_text.lower():
            print("✅ Модель помнит имя пользователя!")
        else:
            print("❌ Модель НЕ помнит имя пользователя")
            
        if "python" in response_text.lower():
            print("✅ Модель помнит про Python!")
        else:
            print("❌ Модель НЕ помнит про Python")
            
        if "django" in response_text.lower() or "fastapi" in response_text.lower():
            print("✅ Модель помнит про фреймворки!")
        else:
            print("❌ Модель НЕ помнит про фреймворки")
            
        if "docker" in response_text.lower() or "kubernetes" in response_text.lower():
            print("✅ Модель помнит про контейнеризацию!")
        else:
            print("❌ Модель НЕ помнит про контейнеризацию")
        
        # Общая оценка
        memory_score = len(found_keywords) / len(context_keywords) * 100
        print(f"\n📈 Оценка памяти: {memory_score:.1f}%")
        
        if memory_score >= 70:
            print("🎉 Отличная память! Модель хорошо помнит контекст")
        elif memory_score >= 40:
            print("👍 Хорошая память! Модель помнит основные детали")
        else:
            print("😞 Слабая память! Модель плохо помнит контекст")
            
    except Exception as e:
        print(f"❌ Ошибка во время тестирования: {e}")
        
    finally:
        await service.disconnect()

if __name__ == "__main__":
    asyncio.run(test_context_memory())
