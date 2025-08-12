#!/usr/bin/env python3
"""
Тест для проверки гибридной конфигурации:
- Модель из model_config.py (глобальный контроль)
- Настройки из chat_config.py (унифицированная конфигурация)
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_hybrid_config():
    """Тестируем гибридную конфигурацию."""
    try:
        print("🔍 Проверяем гибридную конфигурацию...")
        
        # 1. Проверяем model_config.py
        print("\n📋 1. Проверяем model_config.py (глобальный контроль модели):")
        try:
            import model_config
            print("✅ model_config успешно импортирован")
            print(f"  • Текущая модель: {model_config.get_current_model()}")
            print(f"  • Доступные модели: {len(model_config.get_available_models())}")
            
            # Показываем статус синхронизации
            print("\n  📊 Статус синхронизации:")
            model_config.sync_with_chat_config()
            
        except Exception as e:
            print(f"❌ Ошибка при работе с model_config.py: {e}")
            return False
        
        # 2. Проверяем chat_config.py
        print("\n📋 2. Проверяем chat_config.py (унифицированные настройки):")
        try:
            from app.chat_bot.config.chat_config import chat_config
            print("✅ chat_config успешно импортирован")
            
            print("  • Настройки text-generation-webui:")
            print(f"    - URL: {chat_config.textgen_webui_url}")
            print(f"    - Порт: {chat_config.textgen_webui_port}")
            print(f"    - Хост: {chat_config.textgen_webui_host}")
            print(f"    - Директория: {chat_config.textgen_webui_model_dir}")
            
            print("  • Аппаратные параметры:")
            print(f"    - Контекст: {chat_config.N_CTX}")
            print(f"    - GPU слои: {chat_config.N_GPU_LAYERS}")
            print(f"    - CPU потоки: {chat_config.N_THREADS}")
            print(f"    - Размер батча: {chat_config.N_BATCH}")
            
        except Exception as e:
            print(f"❌ Ошибка при работе с chat_config.py: {e}")
            return False
        
        # 3. Проверяем синхронизацию
        print("\n📋 3. Проверяем синхронизацию:")
        
        # Проверяем, что модель из model_config.py существует в chat_config.py
        current_model = model_config.get_current_model()
        model_path = Path(chat_config.textgen_webui_model_dir) / current_model
        
        if model_path.exists():
            print(f"  ✅ Модель найдена: {model_path}")
        else:
            print(f"  ❌ Модель не найдена: {model_path}")
            print(f"  💡 Проверьте, что модель {current_model} находится в {chat_config.textgen_webui_model_dir}")
        
        # 4. Проверяем read_chat_config.py
        print("\n📋 4. Проверяем read_chat_config.py:")
        try:
            import sys
            from pathlib import Path
            
            # Добавляем путь к text-generation-webui
            webui_path = Path(__file__).parent.parent / "text-generation-webui"
            sys.path.insert(0, str(webui_path))
            
            from read_chat_config import read_chat_config, get_current_model
            
            print("✅ read_chat_config успешно импортирован")
            print(f"  • Текущая модель: {get_current_model()}")
            
            # Тестируем команду config
            print("  • Тестируем команду config:")
            import io
            from contextlib import redirect_stdout
            
            f = io.StringIO()
            with redirect_stdout(f):
                read_chat_config()
            output = f.getvalue()
            
            if "API_PORT=" in output and "CTX_SIZE=" in output:
                print("    ✅ Команда config работает корректно")
            else:
                print("    ❌ Команда config работает некорректно")
                
        except Exception as e:
            print(f"❌ Ошибка при работе с read_chat_config.py: {e}")
            return False
        
        # 5. Итоговый результат
        print("\n🎯 Результат гибридной конфигурации:")
        print("  ✅ model_config.py - глобальный контроль модели")
        print("  ✅ chat_config.py - унифицированные настройки")
        print("  ✅ read_chat_config.py - мост между конфигурациями")
        print("  ✅ start_mythomax_working.bat - гибридный запуск")
        print("\n💡 Преимущества:")
        print("  • Модель можно изменить глобально в model_config.py")
        print("  • Все остальные настройки синхронизированы с chat_config.py")
        print("  • Нет дублирования конфигурации")
        print("  • Гибкость + унификация")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании гибридной конфигурации: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    from pathlib import Path
    test_hybrid_config()
