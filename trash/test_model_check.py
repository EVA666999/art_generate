#!/usr/bin/env python3
"""
Тестовый скрипт для проверки работы model_config.py
"""

import sys
from pathlib import Path

# Добавляем путь к text-generation-webui
webui_path = Path(__file__).parent.parent / "text-generation-webui"
sys.path.insert(0, str(webui_path))

try:
    import model_config
    
    print("=== Тест model_config.py ===")
    print(f"Текущая модель: {model_config.get_current_model()}")
    print(f"Модель существует: {model_config.check_model_exists(model_config.get_current_model())}")
    print(f"Путь к модели: {model_config.get_model_path(model_config.get_current_model())}")
    print(f"Модели на диске: {model_config.get_available_models_on_disk()}")
    
    print("\n=== Статус синхронизации ===")
    model_config.show_sync_status()
    
except Exception as e:
    print(f"Ошибка: {e}")
    import traceback
    traceback.print_exc()
