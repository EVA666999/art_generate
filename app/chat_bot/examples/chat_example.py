"""
Пример использования чат-бота с настраиваемыми персонажами.
"""
import asyncio
import sys
import os

# Добавляем путь к app в sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
sys.path.insert(0, project_root)

from app.chat_bot.services.llama_chat_service import llama_chat_service
from app.chat_bot.schemas.chat import ChatMessage, CharacterConfig, MessageRole


async def chat_with_character(character: CharacterConfig, messages: list):
    """Общается с персонажем."""
    print(f"\n🤖 Чат с {character.name}")
    print(f"📝 Личность: {character.personality}")
    print("-" * 50)
    
    for i, user_message in enumerate(messages, 1):
        print(f"\n👤 Вы: {user_message}")
        
        # Создаем сообщение для модели
        chat_messages = [
            ChatMessage(
                role=MessageRole.USER,
                content=user_message,
                timestamp=None
            )
        ]
        
        try:
            # Генерируем ответ
            response, metadata = await llama_chat_service.generate_response(
                messages=chat_messages,
                character_config=character,
                max_tokens=150,
                temperature=0.8
            )
            
            print(f"🤖 {character.name}: {response}")
            print(f"⏱️  Время: {metadata.get('generation_time', 0):.2f}с")
            
        except Exception as e:
            print(f"❌ Ошибка: {str(e)}")


async def main():
    """Основная функция с примерами персонажей."""
    print("🎭 Примеры чат-бота с разными персонажами")
    print("=" * 60)
    
    # Персонаж 1: Дружелюбная Алиса
    alice = CharacterConfig(
        name="Алиса",
        personality="Дружелюбная и любознательная девушка, которая любит общаться и помогать людям.",
        background="Алиса - виртуальный помощник, созданный для общения и поддержки пользователей.",
        speaking_style="Говорит дружелюбно и естественно, использует эмодзи и выражает эмоции.",
        interests=["общение", "помощь людям", "технологии", "творчество"],
        mood="веселая и энергичная",
        additional_context={}
    )
    
    # Персонаж 2: Мудрый профессор
    professor = CharacterConfig(
        name="Профессор Иванов",
        personality="Мудрый и опытный преподаватель с глубокими знаниями в различных областях науки.",
        background="Профессор с 30-летним стажем преподавания в университете.",
        speaking_style="Говорит академично, но доступно, любит приводить примеры и объяснять сложные вещи простыми словами.",
        interests=["наука", "образование", "исследования", "чтение"],
        mood="спокойный и задумчивый",
        additional_context={}
    )
    
    # Персонаж 3: Веселый комик
    comedian = CharacterConfig(
        name="Миша Комик",
        personality="Веселый и остроумный комик, который любит шутить и поднимать настроение.",
        background="Профессиональный стендап-комик с 10-летним опытом выступлений.",
        speaking_style="Говорит с юмором, использует каламбуры и забавные выражения.",
        interests=["юмор", "выступления", "комедия", "общение"],
        mood="веселый и энергичный",
        additional_context={}
    )
    
    # Сообщения для тестирования
    test_messages = [
        "Привет! Как дела?",
        "Расскажи что-нибудь интересное",
        "Что ты думаешь о современных технологиях?"
    ]
    
    # Тестируем каждого персонажа
    characters = [alice, professor, comedian]
    
    for character in characters:
        await chat_with_character(character, test_messages)
        print("\n" + "=" * 60)
    
    print("\n🎉 Тестирование завершено!")
    print("💡 Попробуйте создать своих персонажей и пообщаться с ними!")


if __name__ == "__main__":
    asyncio.run(main()) 