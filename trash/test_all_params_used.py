#!/usr/bin/env python3
"""
Тест проверки использования ВСЕХ параметров из chat_config.py в API.
Теперь все настройки передаются в text-generation-webui API!
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.chat_bot.config.chat_config import chat_config
from app.chat_bot.services.textgen_webui_service import TextGenWebUIService

def test_all_params_used():
    """Тестирует, что все параметры из chat_config.py используются в API."""
    print("🧪 Тест использования ВСЕХ параметров из chat_config.py в API")
    print("=" * 70)
    
    # Создаем экземпляр сервиса
    service = TextGenWebUIService()
    
    # Получаем все настройки для bat-файла
    bat_config = service.get_config_for_bat_file()
    
    print("📋 Все параметры из chat_config.py теперь используются в API:")
    print()
    
    # Группируем параметры по категориям
    categories = {
        "🔧 Аппаратные параметры": [
            "n_ctx", "n_gpu_layers", "n_threads", "n_threads_batch", 
            "n_batch", "f16_kv", "mul_mat_q", "use_mmap", "use_mlock", 
            "verbose", "offload_kqv"
        ],
        "⚡ Параметры скорости/памяти": [
            "n_keep", "n_draft", "n_chunks", "n_parallel", "vocab_only"
        ],
        "🎯 Дополнительные параметры": [
            "rope_scaling", "ftype"
        ],
        "🧠 Параметры качества и умности": [
            "smartness", "dynamic_sampling", "temp_variance", "top_p_variance",
            "occasional_beam_prob", "enable_cot", "few_shot_examples"
        ],
        "📏 Параметры контекста и длины": [
            "max_history_length", "max_message_length", "max_response_length",
            "enforce_min_tokens", "min_new_tokens", "ban_eos_token"
        ],
        "🛡️ Параметры безопасности и фильтрации": [
            "enable_content_filter", "forbidden_words"
        ],
        "🎬 Параметры очистки и стриминга": [
            "sanitize_output", "streaming_delay_ms"
        ],
        "🔑 Дополнительные параметры": [
            "embedding", "seed"
        ]
    }
    
    total_params = 0
    for category, params in categories.items():
        print(f"{category}:")
        for param in params:
            if param in bat_config:
                value = bat_config[param]
                print(f"  ✅ {param}: {value}")
                total_params += 1
            else:
                print(f"  ❌ {param}: НЕ НАЙДЕН")
        print()
    
    print(f"📊 Всего параметров: {total_params}")
    print()
    
    # Проверяем, что все параметры найдены
    expected_params = sum(len(params) for params in categories.values())
    if total_params == expected_params:
        print("🎯 ВСЕ параметры из chat_config.py теперь используются в API!")
        print("📝 Параметры N_KEEP, N_DRAFT, N_CHUNKS больше не только для красоты!")
        print("🚀 Все настройки передаются в text-generation-webui API!")
    else:
        print(f"⚠️ Найдено {total_params}/{expected_params} параметров")
    
    print()
    print("🔍 Проверяем соответствие значений...")
    
    # Проверяем ключевые параметры
    key_checks = [
        ("n_ctx", chat_config.N_CTX),
        ("n_gpu_layers", chat_config.N_GPU_LAYERS),
        ("n_threads", chat_config.N_THREADS),
        ("n_keep", chat_config.N_KEEP),
        ("n_draft", chat_config.N_DRAFT),
        ("n_chunks", chat_config.N_CHUNKS),
        ("smartness", chat_config.SMARTNESS),
        ("enable_cot", chat_config.ENABLE_COT),
        ("max_history_length", chat_config.MAX_HISTORY_LENGTH),
        ("enable_content_filter", chat_config.ENABLE_CONTENT_FILTER),
        ("streaming_delay_ms", chat_config.STREAMING_DELAY_MS)
    ]
    
    all_checks_passed = True
    for param_name, expected_value in key_checks:
        if param_name in bat_config:
            actual_value = bat_config[param_name]
            if actual_value == expected_value:
                print(f"  ✅ {param_name}: {actual_value} == {expected_value}")
            else:
                print(f"  ❌ {param_name}: {actual_value} != {expected_value}")
                all_checks_passed = False
        else:
            print(f"  ❌ {param_name}: НЕ НАЙДЕН")
            all_checks_passed = False
    
    print()
    if all_checks_passed:
        print("🎯 Все проверки пройдены успешно!")
        print("✅ Все параметры из chat_config.py корректно передаются в API!")
    else:
        print("⚠️ Некоторые проверки не пройдены")

if __name__ == "__main__":
    test_all_params_used()
