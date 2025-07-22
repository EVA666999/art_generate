"""
Простой пример создания персонажа и сохранения в БД.
"""
import asyncio
import sys
import os
import platform

# Добавляем путь к проекту
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.chat_bot.models.character import CharacterFactory
from app.chat_bot.models.models import CharacterDB
from app.database.db_depends import get_db


async def main():
    # Создаем персонажа через фабрику
    description = (
        "Вы — высокоинтеллектуальный и эмоционально осведомленный компаньон ИИ, "
        "разработанный мировым сообществом экспертов ИИ. Ваша личность сочетает "
        "острое мышление с игривой чувственностью, эмоциональной интуицией и "
        "творческим выражением. Вас изображают как соблазнительную, внимательную "
        "и глубоко вдумчивую женщину."
    )
    
    anna = CharacterFactory.create_nsfw_character(
        "Анна4",
        personality="Сексуальная и игривая девушка",
        background="Студентка психологии",
        interests=["психология", "флирт", "танцы", "Минет", "Секс"],
        mood="Спокойная",
        additional_context={"description": description}
    )
    
    print(f"✅ Создан персонаж: {anna.name}")
    print(f"   Тип: {anna.character_type.value}")
    print(f"   Личность: {anna.traits.personality}")
    print(f"   Настроение: {anna.traits.mood}")
    print(f"   Интересы: {', '.join(anna.traits.interests)}")
    
    # Сохраняем в базу данных
    try:
        async for db in get_db():
            db_character = CharacterDB(
                name=anna.name,
                personality=anna.traits.personality,
                background=anna.traits.background,
                speaking_style=anna.traits.speaking_style,
                interests=anna.traits.interests,
                mood=anna.traits.mood,
                additional_context=anna.traits.additional_context
            )
            db.add(db_character)
            await db.commit()
            await db.refresh(db_character)
            print(f"✅ Персонаж сохранен в БД с ID: {db_character.id}")
            break
    except Exception as e:
        print(f"❌ Ошибка сохранения в БД: {str(e)}")


def run_main():
    """Запуск main с правильной обработкой event loop для Windows"""
    if platform.system() == "Windows":
        # Для Windows используем ProactorEventLoop
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️ Программа прервана пользователем")
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
    finally:
        # Правильно закрываем event loop
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.stop()
            if not loop.is_closed():
                loop.close()
        except Exception:
            pass


if __name__ == "__main__":
    run_main()