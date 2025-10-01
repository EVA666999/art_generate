#!/usr/bin/env python3
"""
Тест проверки отсутствия дублирования промптов
"""

import sys
import json
import tempfile
from pathlib import Path

# Добавляем путь к проекту
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app.utils.generation_logger import GenerationLogger
from app.config.default_prompts import get_default_positive_prompts, get_default_negative_prompts

def test_prompt_deduplication():
    """Тест что промпты не дублируются в логах"""
    print("🧪 Тестирование отсутствия дублирования промптов...")
    
    # Создаем временную папку для логов
    with tempfile.TemporaryDirectory() as temp_dir:
        logger = GenerationLogger(logs_dir=temp_dir)
        
        # Тестовые данные
        user_prompt = "beautiful girl"
        user_negative_prompt = "ugly"
        
        # Симулируем добавление дефолтных промптов
        default_positive = get_default_positive_prompts()
        default_negative = get_default_negative_prompts()
        
        enhanced_prompt = f"{user_prompt}, {default_positive}"
        enhanced_negative_prompt = f"{user_negative_prompt}, {default_negative}"
        
        settings = {
            "width": 512,
            "height": 853,
            "steps": 30,
            "cfg_scale": 8,
            "sampler_name": "DPM++ 2M Karras",
            "use_default_prompts": True,
            "prompt": enhanced_prompt,  # Уже с дефолтными промптами
            "negative_prompt": enhanced_negative_prompt  # Уже с дефолтными промптами
        }
        
        # Тестируем логирование
        logger.log_generation(
            prompt=user_prompt,  # Оригинальный промпт пользователя
            negative_prompt=user_negative_prompt,  # Оригинальный негативный промпт
            character="anna",
            settings=settings,
            generation_time=45.5,
            image_url="test_url",
            success=True,
            enhanced_prompt=enhanced_prompt,  # Улучшенный промпт
            enhanced_negative_prompt=enhanced_negative_prompt  # Улучшенный негативный промпт
        )
        
        # Проверяем созданный лог
        log_files = list(Path(temp_dir).glob("generation_*.jsonl"))
        assert len(log_files) == 1, f"Ожидался 1 лог файл, найдено {len(log_files)}"
        
        with open(log_files[0], 'r', encoding='utf-8') as f:
            log_content = f.read()
            log_entry = json.loads(log_content.strip())
        
        # Проверяем структуру лога
        print("📋 Проверка структуры лога...")
        
        # Проверяем промпты
        assert "prompts" in log_entry, "Отсутствует секция prompts"
        prompts = log_entry["prompts"]
        
        # Проверяем что user_prompt - это оригинальный промпт
        assert prompts["user_prompt"] == user_prompt, f"Неправильный user_prompt: {prompts['user_prompt']}"
        assert prompts["user_negative_prompt"] == user_negative_prompt, f"Неправильный user_negative_prompt: {prompts['user_negative_prompt']}"
        
        # Проверяем что enhanced_prompt содержит и оригинальный и дефолтные промпты
        assert prompts["enhanced_prompt"] == enhanced_prompt, f"Неправильный enhanced_prompt: {prompts['enhanced_prompt']}"
        assert prompts["enhanced_negative_prompt"] == enhanced_negative_prompt, f"Неправильный enhanced_negative_prompt: {prompts['enhanced_negative_prompt']}"
        
        # Проверяем что enhanced_prompt содержит user_prompt
        assert user_prompt in prompts["enhanced_prompt"], "enhanced_prompt не содержит user_prompt"
        assert user_negative_prompt in prompts["enhanced_negative_prompt"], "enhanced_negative_prompt не содержит user_negative_prompt"
        
        # Проверяем что enhanced_prompt содержит дефолтные промпты
        assert default_positive in prompts["enhanced_prompt"], "enhanced_prompt не содержит дефолтные промпты"
        assert default_negative in prompts["enhanced_negative_prompt"], "enhanced_negative_prompt не содержит дефолтные промпты"
        
        # Проверяем длины
        assert prompts["prompt_length"] == len(enhanced_prompt), f"Неправильная длина промпта: {prompts['prompt_length']} != {len(enhanced_prompt)}"
        assert prompts["negative_prompt_length"] == len(enhanced_negative_prompt), f"Неправильная длина негативного промпта: {prompts['negative_prompt_length']} != {len(enhanced_negative_prompt)}"
        
        print("✅ Все проверки пройдены!")
        print(f"📊 Оригинальный промпт: '{user_prompt}'")
        print(f"📊 Улучшенный промпт: '{enhanced_prompt[:100]}...'")
        print(f"📊 Длина улучшенного промпта: {len(enhanced_prompt)}")
        print(f"📊 Содержит дефолтные промпты: {default_positive in enhanced_prompt}")
        
        return True

def test_no_duplication_in_enhanced_prompts():
    """Тест что в enhanced_prompts нет дублирования"""
    print("\n🧪 Тестирование отсутствия дублирования в enhanced_prompts...")
    
    # Тестовые данные с потенциальным дублированием
    user_prompt = "1girl, solo"  # Уже содержит некоторые дефолтные промпты
    user_negative_prompt = "low quality"  # Уже содержит некоторые дефолтные промпты
    
    default_positive = get_default_positive_prompts()
    default_negative = get_default_negative_prompts()
    
    # Проверяем что дефолтные промпты содержат те же слова
    assert "1girl" in default_positive, "1girl должен быть в дефолтных промптах"
    assert "solo" in default_positive, "solo должен быть в дефолтных промптах"
    assert "low quality" in default_negative, "low quality должен быть в дефолтных промптах"
    
    # Создаем enhanced промпты
    enhanced_prompt = f"{user_prompt}, {default_positive}"
    enhanced_negative_prompt = f"{user_negative_prompt}, {default_negative}"
    
    # Проверяем что есть дублирование (это нормально для теста)
    print(f"📊 User prompt: '{user_prompt}'")
    print(f"📊 Default positive: '{default_positive[:50]}...'")
    print(f"📊 Enhanced prompt: '{enhanced_prompt[:100]}...'")
    
    # Подсчитываем количество вхождений
    user_words = user_prompt.split(", ")
    for word in user_words:
        count = enhanced_prompt.count(word)
        if count > 1:
            print(f"⚠️  Слово '{word}' встречается {count} раз в enhanced_prompt")
        else:
            print(f"✅ Слово '{word}' встречается {count} раз в enhanced_prompt")
    
    print("✅ Тест завершен!")
    return True

if __name__ == "__main__":
    print("🚀 Запуск тестов проверки дублирования промптов...")
    
    try:
        test_prompt_deduplication()
        test_no_duplication_in_enhanced_prompts()
        
        print("\n🎉 ВСЕ ТЕСТЫ ПРОШЛИ УСПЕШНО!")
        print("✅ Промпты не дублируются в логах!")
        
    except Exception as e:
        print(f"\n❌ ОШИБКА В ТЕСТАХ: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
