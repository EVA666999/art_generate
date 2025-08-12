#!/usr/bin/env python3
"""
Простой тест конфигурации chat_config.py
"""

def test_config_values():
    """Тестирует значения конфигурации."""
    print("🧪 Простой тест конфигурации chat_config.py")
    print("=" * 50)
    
    # Проверяем, что файл существует и читается
    try:
        with open('../app/chat_bot/config/chat_config.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("✅ Файл chat_config.py успешно прочитан")
        
        # Проверяем наличие ключевых параметров
        key_params = [
            'N_CTX', 'N_GPU_LAYERS', 'N_THREADS', 'N_BATCH',
            'N_KEEP', 'N_DRAFT', 'N_CHUNKS', 'N_PARALLEL',
            'F16_KV', 'MUL_MAT_Q', 'USE_MMAP', 'OFFLOAD_KQV'
        ]
        
        found_params = []
        for param in key_params:
            if param in content:
                found_params.append(param)
                print(f"  ✅ {param} найден")
            else:
                print(f"  ❌ {param} НЕ найден")
        
        print(f"\n📊 Найдено параметров: {len(found_params)}/{len(key_params)}")
        
        if len(found_params) == len(key_params):
            print("🎯 Все параметры найдены! Конфигурация готова к использованию.")
        else:
            print("⚠️ Некоторые параметры отсутствуют.")
            
    except FileNotFoundError:
        print("❌ Файл chat_config.py не найден")
    except Exception as e:
        print(f"❌ Ошибка при чтении файла: {e}")

if __name__ == "__main__":
    test_config_values()
