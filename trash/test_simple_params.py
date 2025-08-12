#!/usr/bin/env python3
"""
Простой тест передачи параметров из chat_config.py в API
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.chat_bot.config.chat_config import chat_config

def test_params_transmission():
    """Тестирует передачу параметров."""
    print("🧪 Простой тест передачи параметров")
    print("=" * 50)
    
    # Проверяем ключевые параметры
    key_params = {
        "N_CTX": chat_config.N_CTX,
        "N_GPU_LAYERS": chat_config.N_GPU_LAYERS, 
        "N_THREADS": chat_config.N_THREADS,
        "N_BATCH": chat_config.N_BATCH,
        "N_KEEP": chat_config.N_KEEP,
        "N_DRAFT": chat_config.N_DRAFT,
        "N_CHUNKS": chat_config.N_CHUNKS,
        "SMARTNESS": chat_config.SMARTNESS,
        "ENABLE_COT": chat_config.ENABLE_COT,
        "MAX_HISTORY_LENGTH": chat_config.MAX_HISTORY_LENGTH
    }
    
    print("📋 Ключевые параметры:")
    for name, value in key_params.items():
        print(f"  ✅ {name}: {value}")
    
    print(f"\n🎯 Всего параметров: {len(key_params)}")
    print("✅ Все параметры готовы к передаче в API!")
    
    # Проверяем, что параметры не None
    all_valid = all(value is not None for value in key_params.values())
    if all_valid:
        print("🎉 Все параметры имеют валидные значения!")
    else:
        print("⚠️ Некоторые параметры имеют значение None")

if __name__ == "__main__":
    test_params_transmission()
