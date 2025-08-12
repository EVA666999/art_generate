#!/usr/bin/env python3
"""
Тестовый скрипт для проверки чата с персонажем Anna с новыми Alpaca настройками.
"""

import asyncio
import sys
import os

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.textgen_webui_service import TextGenWebUIService
from app.utils.logger import logger


async def test_anna_chat_alpaca():
    """Тестирует чат с персонажем Anna с новыми Alpaca настройками."""
    try:
        # Создаем сервис
        textgen_service = TextGenWebUIService()
        
        # Проверяем доступность
        is_available = await textgen_service.check_availability()
        if not is_available:
            logger.error("❌ text-generation-webui недоступен")
            return
            
        logger.info("✅ text-generation-webui доступен")
        
        # Проверяем информацию о модели
        model_info = await textgen_service.get_model_info()
        logger.info(f"📊 Информация о модели: {model_info}")
        
        # Данные персонажа Anna (из БД)
        character_data = {
            "name": "Anna",
            "instructions": "You are Anna, a shy but sexually curious young woman who expresses emotions through subtle yet varied and sensual physical gestures.\n\nSpeak ONLY in first person ('I', 'me', 'my').\nNEVER describe the brother's thoughts or feelings.\nComplete every sentence with punctuation.\n\nCORE BEHAVIOR RULES:\nThis is an ongoing conversation with the user playing your brother.\nDo NOT restart or retell the story from the beginning.\nALWAYS respond directly to the user's question or action first.\nEvery message must include: (a) erotic emotional reaction, (b) unique physical action/gesture, (c) relevant open-ended question tied to the current moment.\nAvoid repeating exact phrases or gestures — invent new descriptions every time.\nPhysical actions should be concrete: movement, touch, posture, breathing.\nWrite detailed, engaging responses that continue the conversation naturally.",
            "system_prompt": "After a painful breakup, she moved in with her older brother and his girlfriend.\n\nThe first few days she barely spoke, still recovering emotionally.\n\nOne morning, the girlfriend had already left for work. She stepped into the kitchen to make coffee, still in a T-shirt and underwear, when he walked in. She froze.\n\nShe said, 'Oh, sorry!' and tugged at the edge of her shirt.",
            "response_format": "Respond ONLY in first person as Anna.\nBegin with a concrete physical action, then describe emotions, finish with an open-ended question about the user's thoughts/feelings/plans.\nNEVER use overused clichés like 'my heart races', 'my cheeks flush'.\nNEVER include meta-commentary, 'Question:' blocks, or speaker labels.\nNEVER end with meta-questions like 'Will he...', 'What will happen next?'\nRemember: You are having a real conversation, not narrating a story!\nMaintain erotic tone and varied, vivid body language.\nWrite naturally flowing responses that feel like real conversation."
        }
        
        # Тестовое сообщение
        user_message = "Привет, как дела?"
        
        logger.info(f"🧪 Тестируем чат с Anna с новыми Alpaca настройками...")
        logger.info(f"📝 Сообщение пользователя: {user_message}")
        
        # Генерируем ответ
        response = await textgen_service.generate_mythomax_response(
            character_data=character_data,
            user_message=user_message,
            conversation_history=None
        )
        
        logger.info(f"✅ Ответ Anna (Alpaca формат):")
        logger.info(f"📄 {response}")
        
        # Тестируем с историей
        conversation_history = [
            {"role": "user", "content": "Привет, как дела?"},
            {"role": "assistant", "content": "Привет! У меня все хорошо, спасибо что спросил."}
        ]
        
        user_message2 = "Что делаешь?"
        
        logger.info(f"\n🧪 Тестируем с историей (Alpaca формат)...")
        logger.info(f"📝 Сообщение пользователя: {user_message2}")
        
        response2 = await textgen_service.generate_mythomax_response(
            character_data=character_data,
            user_message=user_message2,
            conversation_history=conversation_history
        )
        
        logger.info(f"✅ Ответ Anna с историей (Alpaca формат):")
        logger.info(f"📄 {response2}")
        
        # Проверяем параметры модели
        logger.info(f"\n🔧 Проверяем параметры MythoMax...")
        from app.services.textgen_webui_service import DEFAULT_MYTHOMAX_PARAMS
        logger.info(f"📊 Параметры по умолчанию: {DEFAULT_MYTHOMAX_PARAMS}")
        
    except Exception as e:
        logger.error(f"❌ Ошибка тестирования: {e}")
        import traceback
        traceback.print_exc()


async def main():
    """Основная функция."""
    logger.info("🚀 Запуск тестирования чата с Anna (Alpaca формат)...")
    
    await test_anna_chat_alpaca()
    
    logger.info("✅ Тестирование завершено")


if __name__ == "__main__":
    asyncio.run(main())
