#!/usr/bin/env python3
"""
Тест для проверки скрытого сообщения в чате.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from app.chat_bot.streaming.chat_processor import ChatProcessor
from app.chat_bot.config.chat_config import chat_config
from app.chat_bot.models.characters.anna import get_character_data


def test_hidden_message_in_prompt():
    """Тест проверяет, что скрытое сообщение добавляется к пользовательским сообщениям."""
    
    # Создаем процессор чата
    processor = ChatProcessor()
    
    # Получаем данные персонажа
    character_data = get_character_data()
    
    # Тестовое сообщение пользователя
    user_message = "Привет, как дела?"
    
    # История чата
    history = [
        {"role": "user", "content": "Как дела?"},
        {"role": "assistant", "content": "Отлично, спасибо!"}
    ]
    
    # Строим промпт с включенным скрытым сообщением
    prompt_with_hidden = processor.build_prompt(
        user_message, 
        history, 
        character_data, 
        is_continue_story=False,
        chat_config=chat_config
    )
    
    # Проверяем, что скрытое сообщение добавлено
    hidden_message = chat_config.HIDDEN_USER_MESSAGE
    assert hidden_message in prompt_with_hidden, f"Скрытое сообщение '{hidden_message}' не найдено в промпте"
    
    # Проверяем, что скрытое сообщение добавлено к текущему сообщению
    assert f"### Instruction:\n{user_message}\n\n{hidden_message}\n\n### Response:" in prompt_with_hidden, \
        "Скрытое сообщение не добавлено к текущему сообщению пользователя"
    
    # Проверяем, что скрытое сообщение добавлено к историческим сообщениям
    assert f"### Instruction:\nКак дела?\n\n{hidden_message}\n\n### Response:" in prompt_with_hidden, \
        "Скрытое сообщение не добавлено к историческим сообщениям пользователя"
    
    print("✅ Тест пройден: скрытое сообщение добавляется к пользовательским сообщениям")


def test_hidden_message_disabled():
    """Тест проверяет, что при отключенном скрытом сообщении оно не добавляется."""
    
    # Создаем процессор чата
    processor = ChatProcessor()
    
    # Получаем данные персонажа
    character_data = get_character_data()
    
    # Создаем конфиг с отключенным скрытым сообщением
    from app.chat_bot.config.chat_config import ChatConfig
    test_config = ChatConfig()
    test_config.ENABLE_HIDDEN_MESSAGE = False
    
    # Тестовое сообщение пользователя
    user_message = "Привет, как дела?"
    
    # Строим промпт с отключенным скрытым сообщением
    prompt_without_hidden = processor.build_prompt(
        user_message, 
        [], 
        character_data, 
        is_continue_story=False,
        chat_config=test_config
    )
    
    # Проверяем, что скрытое сообщение НЕ добавлено
    hidden_message = test_config.HIDDEN_USER_MESSAGE
    assert hidden_message not in prompt_without_hidden, f"Скрытое сообщение '{hidden_message}' найдено в промпте, хотя должно быть отключено"
    
    print("✅ Тест пройден: скрытое сообщение не добавляется при отключенной настройке")


def test_hidden_message_config():
    """Тест проверяет конфигурацию скрытого сообщения."""
    
    # Проверяем, что настройки существуют
    assert hasattr(chat_config, 'HIDDEN_USER_MESSAGE'), "HIDDEN_USER_MESSAGE не найдено в конфиге"
    assert hasattr(chat_config, 'ENABLE_HIDDEN_MESSAGE'), "ENABLE_HIDDEN_MESSAGE не найдено в конфиге"
    
    # Проверяем значения по умолчанию
    assert chat_config.ENABLE_HIDDEN_MESSAGE == True, "ENABLE_HIDDEN_MESSAGE должно быть True по умолчанию"
    assert chat_config.HIDDEN_USER_MESSAGE == "don't write time at the end of a sentence", \
        f"Неправильное значение HIDDEN_USER_MESSAGE: {chat_config.HIDDEN_USER_MESSAGE}"
    
    print("✅ Тест пройден: конфигурация скрытого сообщения корректна")


if __name__ == "__main__":
    print("🧪 Запуск тестов скрытого сообщения...")
    
    try:
        test_hidden_message_config()
        test_hidden_message_in_prompt()
        test_hidden_message_disabled()
        
        print("\n🎉 Все тесты пройдены успешно!")
        print("✅ Скрытое сообщение работает корректно")
        
    except Exception as e:
        print(f"\n❌ Ошибка в тестах: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
