#!/usr/bin/env python3
"""
Полный тест всех параметров из chat_config.py
Проверяет существование, валидность и доступность всех параметров
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.chat_bot.config.chat_config import chat_config

def test_all_params():
    """Тестирует все параметры из chat_config.py."""
    print("🧪 ПОЛНЫЙ ТЕСТ ВСЕХ ПАРАМЕТРОВ")
    print("=" * 60)
    
    # Получаем все атрибуты конфигурации
    config_attrs = [attr for attr in dir(chat_config) if not attr.startswith('_')]
    
    # Группируем параметры по категориям
    categories = {
        "API настройки": [
            "TEXTGEN_WEBUI_ENABLED", "TEXTGEN_WEBUI_URL", 
            "TEXTGEN_WEBUI_TIMEOUT", "TEXTGEN_WEBUI_MODEL"
        ],
        "Аппаратные параметры": [
            "N_CTX", "N_GPU_LAYERS", "N_THREADS", "N_THREADS_BATCH", 
            "N_BATCH", "F16_KV", "MUL_MAT_Q", "USE_MMAP", "USE_MLOCK", 
            "VERBOSE", "OFFLOAD_KQV"
        ],
        "Скорость/память": [
            "N_KEEP", "N_DRAFT", "N_CHUNKS", "N_PARALLEL", "VOCAB_ONLY"
        ],
        "Генерация": [
            "DEFAULT_MAX_TOKENS", "DEFAULT_TEMPERATURE", "DEFAULT_TOP_P", 
            "DEFAULT_TOP_K", "DEFAULT_REPEAT_PENALTY", "DEFAULT_PRESENCE_PENALTY",
            "DEFAULT_STOP_TOKENS"
        ],
        "Контекст/длина": [
            "MAX_HISTORY_LENGTH", "MAX_MESSAGE_LENGTH", "MAX_CHARACTER_NAME_LENGTH",
            "MAX_RESPONSE_LENGTH", "ENFORCE_MIN_TOKENS", "MIN_NEW_TOKENS", "BAN_EOS_TOKEN"
        ],
        "Качество/умность": [
            "SMARTNESS", "DYNAMIC_SAMPLING", "TEMP_VARIANCE", "TOP_P_VARIANCE",
            "OCCASIONAL_BEAM_PROB", "ENABLE_COT", "FEW_SHOT_EXAMPLES"
        ],
        "Безопасность": [
            "ENABLE_CONTENT_FILTER", "FORBIDDEN_WORDS", "SANITIZE_OUTPUT"
        ],
        "Логирование/кэш": [
            "LOG_CHAT_REQUESTS", "LOG_CHAT_RESPONSES", "ENABLE_CACHE",
            "CACHE_TTL", "MAX_CACHE_SIZE"
        ],
        "Стриминг": [
            "STREAMING_DELAY_MS"
        ],
        "Прочее": [
            "SEED", "EMBEDDING", "ROPE_SCALING", "FTYPE"
        ]
    }
    
    total_params = 0
    valid_params = 0
    missing_params = []
    
    print("📋 Проверка параметров по категориям:")
    print()
    
    for category, params in categories.items():
        print(f"🔹 {category}:")
        category_valid = 0
        
        for param in params:
            total_params += 1
            
            try:
                value = getattr(chat_config, param)
                if value is not None:
                    print(f"  ✅ {param}: {value}")
                    category_valid += 1
                    valid_params += 1
                else:
                    print(f"  ⚠️ {param}: None")
                    missing_params.append(param)
            except AttributeError:
                print(f"  ❌ {param}: НЕ СУЩЕСТВУЕТ!")
                missing_params.append(param)
        
        print(f"  📊 Валидных: {category_valid}/{len(params)}")
        print()
    
    print("=" * 60)
    print(f"📊 ИТОГОВАЯ СТАТИСТИКА:")
    print(f"  🎯 Всего параметров: {total_params}")
    print(f"  ✅ Валидных: {valid_params}")
    print(f"  ❌ Проблемных: {len(missing_params)}")
    
    if missing_params:
        print(f"\n⚠️ ПРОБЛЕМНЫЕ ПАРАМЕТРЫ:")
        for param in missing_params:
            print(f"  - {param}")
    
    # Проверяем дополнительные атрибуты
    print(f"\n🔍 ДОПОЛНИТЕЛЬНЫЕ АТРИБУТЫ:")
    additional_attrs = [attr for attr in config_attrs if attr not in [param for params in categories.values() for param in params]]
    for attr in additional_attrs:
        if not attr.startswith('_'):
            try:
                value = getattr(chat_config, attr)
                print(f"  📝 {attr}: {type(value).__name__}")
            except:
                print(f"  ❌ {attr}: ошибка доступа")
    
    print(f"\n🎉 Тест завершен! Все параметры проверены.")

if __name__ == "__main__":
    test_all_params()
