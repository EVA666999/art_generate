"""
Тест новых файлов настроек
"""
import sys
from pathlib import Path

# Добавляем корень проекта в путь
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.config.generation_defaults import DEFAULT_GENERATION_PARAMS, ADETAILER_SETTINGS
from app.config.default_prompts import get_default_positive_prompts, get_default_negative_prompts

def test_settings():
    """Тестирует текущие настройки"""
    print(f"Основные steps: {DEFAULT_GENERATION_PARAMS['steps']}")
    print(f"Основной sampler: {DEFAULT_GENERATION_PARAMS['sampler_name']}")
    print(f"ADetailer steps: {ADETAILER_SETTINGS['ad_steps']}")
    print(f"ADetailer model: {ADETAILER_SETTINGS['ad_model']}")
    print(f"ADetailer prompt: {ADETAILER_SETTINGS['prompt'][:50]}...")

def update_adetailer_steps(new_steps: int):
    """Обновляет steps в ADetailer (только для теста)"""
    global ADETAILER_SETTINGS
    ADETAILER_SETTINGS['ad_steps'] = new_steps
    print(f"ADetailer steps обновлены на {new_steps}")

def get_complete_payload():
    """Получает полный payload для тестирования"""
    import copy
    payload = copy.deepcopy(DEFAULT_GENERATION_PARAMS)
    return payload

def main():
    """Главная функция теста"""
    print("=" * 60)
    print("ТЕСТ НОВЫХ ФАЙЛОВ НАСТРОЕК")
    print("=" * 60)
    
    # Тест 1: Проверяем текущие настройки
    print("\n1. Текущие настройки:")
    test_settings()
    
    # Тест 2: Изменяем настройки ADetailer
    print("\n2. Изменяем ADetailer steps на 100:")
    update_adetailer_steps(100)
    test_settings()
    
    # Тест 3: Изменяем на 200
    print("\n3. Изменяем ADetailer steps на 200:")
    update_adetailer_steps(200)
    test_settings()
    
    # Тест 4: Проверяем полный payload
    print("\n4. Полный payload:")
    payload = get_complete_payload()
    adetailer_args = payload["alwayson_scripts"]["ADetailer"]["args"]
    print(f"   Основные steps: {payload['steps']}")
    print(f"   ADetailer enabled: {adetailer_args[0]}")
    print(f"   ADetailer steps: {adetailer_args[1]['ad_steps']}")
    print(f"   ADetailer model: {adetailer_args[1]['ad_model']}")
    
    # Тест 5: Проверяем промпты
    print("\n5. Дефолтные промпты:")
    print(f"   Позитивные: {get_default_positive_prompts()[:50]}...")
    print(f"   Негативные: {get_default_negative_prompts()[:50]}...")
    
    print("\n" + "=" * 60)
    print("ТЕСТ ЗАВЕРШЕН")
    print("=" * 60)

if __name__ == "__main__":
    main() 