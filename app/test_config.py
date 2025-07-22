"""
Простой тест для проверки динамического чтения настроек
"""
import sys
from pathlib import Path

# Добавляем корень проекта в путь
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.config.shared_config import get_adetailer_settings, get_default_generation_params

def test_dynamic_settings():
    """Тест динамического чтения настроек"""
    print("=" * 60)
    print("ТЕСТ ДИНАМИЧЕСКОГО ЧТЕНИЯ НАСТРОЕК")
    print("=" * 60)
    
    # Тест 1: Чтение настроек ADetailer
    print("\n1. Чтение настроек ADetailer:")
    adetailer_settings = get_adetailer_settings()
    print(f"   ad_steps: {adetailer_settings.get('ad_steps', 'NOT SET')}")
    print(f"   ad_model: {adetailer_settings.get('ad_model', 'NOT SET')}")
    print(f"   ad_denoising_strength: {adetailer_settings.get('ad_denoising_strength', 'NOT SET')}")
    
    # Тест 2: Получение дефолтных параметров генерации
    print("\n2. Получение дефолтных параметров генерации:")
    default_params = get_default_generation_params()
    
    # Проверяем ADetailer в дефолтных параметрах
    if "alwayson_scripts" in default_params and "ADetailer" in default_params["alwayson_scripts"]:
        adetailer_config = default_params["alwayson_scripts"]["ADetailer"]
        if len(adetailer_config.get('args', [])) > 1:
            adetailer_settings_in_payload = adetailer_config['args'][1]
            print(f"   ADetailer steps в payload: {adetailer_settings_in_payload.get('ad_steps', 'NOT SET')}")
            print(f"   ADetailer model в payload: {adetailer_settings_in_payload.get('ad_model', 'NOT SET')}")
        else:
            print("   ADetailer args не найдены")
    else:
        print("   ADetailer не найден в alwayson_scripts")
    
    print(f"   Основные steps: {default_params.get('steps', 'NOT SET')}")
    
    print("\n" + "=" * 60)
    print("ТЕСТ ЗАВЕРШЕН")
    print("=" * 60)

if __name__ == "__main__":
    test_dynamic_settings() 