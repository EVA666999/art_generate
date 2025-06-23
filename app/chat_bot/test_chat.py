"""
Простой тест для проверки работы чат-бота с llama-cpp-python.
"""
import asyncio
import sys
import os

# Добавляем путь к app в sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

from app.chat_bot.services.llama_chat_service import llama_chat_service
from app.chat_bot.schemas.chat import ChatMessage, CharacterConfig, MessageRole


async def test_chat():
    """Тестирует работу чат-бота."""
    print("🚀 Запуск теста чат-бота...")
    
    # Создаем конфигурацию персонажа
    character = CharacterConfig(
        name="Алиса",
        personality="Дружелюбная и любознательная девушка, которая любит общаться и помогать людям.",
        background="Алиса - виртуальный помощник, созданный для общения и поддержки пользователей.",
        speaking_style="Говорит дружелюбно и естественно, использует эмодзи и выражает эмоции.",
        interests=["общение", "помощь людям", "технологии", "творчество"],
        mood="веселая и энергичная",
        additional_context={}
    )
    
    # Создаем сообщения
    messages = [
        ChatMessage(
            role=MessageRole.USER,
            content="Привет! Как дела?",
            timestamp=None
        )
    ]
    
    try:
        print("📝 Генерируем ответ...")
        response, metadata = await llama_chat_service.generate_response(
            messages=messages,
            character_config=character,
            max_tokens=100,
            temperature=0.8
        )
        
        print(f"✅ Ответ получен!")
        print(f"👤 Персонаж: {character.name}")
        print(f"💬 Ответ: {response}")
        print(f"⏱️  Время генерации: {metadata.get('generation_time', 0):.2f} сек")
        print(f"🔢 Токенов использовано: {metadata.get('tokens_used', 'N/A')}")
        
    except Exception as e:
        print(f"❌ Ошибка: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_chat()) 