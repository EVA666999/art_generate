#!/usr/bin/env python3
"""
Тест исправленных параметров из chat_config.py
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from app.chat_bot.config.chat_config import chat_config
    print("✅ chat_config успешно импортирован")
except Exception as e:
    print(f"❌ Ошибка импорта chat_config: {e}")
    sys.exit(1)

def test_critical_params():
    """Тестирует критические параметры."""
    print("\n🧪 Тест критических параметров")
    print("=" * 40)
    
    # Параметры, которые вызывали ошибки
    critical_params = {
        "FEW_SHOT_EXAMPLES": chat_config.FEW_SHOT_EXAMPLES,
        "SEED": chat_config.SEED,
        "N_CTX": chat_config.N_CTX,
        "N_GPU_LAYERS": chat_config.N_GPU_LAYERS,
        "SMARTNESS": chat_config.SMARTNESS,
        "ENABLE_COT": chat_config.ENABLE_COT
    }
    
    for name, value in critical_params.items():
        if value is not None:
            print(f"  ✅ {name}: {value}")
        else:
            print(f"  ⚠️ {name}: None")
    
    # Проверяем типы
    print(f"\n🔍 Проверка типов:")
    print(f"  SEED: {type(chat_config.SEED).__name__} = {chat_config.SEED}")
    print(f"  FEW_SHOT_EXAMPLES: {type(chat_config.FEW_SHOT_EXAMPLES).__name__}")
    
    # Проверяем логику seed
    if chat_config.SEED == -1:
        print("  🎲 SEED = -1 (случайный)")
    else:
        print(f"  🔒 SEED = {chat_config.SEED} (фиксированный)")
    
    print("\n🎉 Тест завершен!")

if __name__ == "__main__":
    test_critical_params()
