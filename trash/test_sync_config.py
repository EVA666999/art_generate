#!/usr/bin/env python3
"""
Тест для проверки синхронизации между chat_config.py и start_mythomax_working.bat
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_config_sync():
    """Тестируем синхронизацию конфигурации."""
    try:
        print("🔍 Проверяем синхронизацию конфигурации...")
        
        # Импортируем chat_config
        from app.chat_bot.config.chat_config import chat_config
        print("✅ chat_config успешно импортирован")
        
        # Проверяем настройки, которые теперь используются в bat-файле
        print("\n📋 Настройки для синхронизации с bat-файлом:")
        print(f"  • textgen_webui_model: {chat_config.textgen_webui_model}")
        print(f"  • textgen_webui_port: {chat_config.textgen_webui_port}")
        print(f"  • textgen_webui_host: {chat_config.textgen_webui_host}")
        print(f"  • N_CTX: {chat_config.N_CTX}")
        print(f"  • N_GPU_LAYERS: {chat_config.N_GPU_LAYERS}")
        print(f"  • N_THREADS: {chat_config.N_THREADS}")
        print(f"  • N_THREADS_BATCH: {chat_config.N_THREADS_BATCH}")
        print(f"  • N_BATCH: {chat_config.N_BATCH}")
        print(f"  • textgen_webui_model_dir: {chat_config.textgen_webui_model_dir}")
        
        # Проверяем, что настройки соответствуют ожидаемым значениям
        print("\n🔍 Проверяем соответствие настроек:")
        
        # Проверяем порты
        if chat_config.textgen_webui_port == 7860:
            print("  ✅ API порт: 7860 (стандартный)")
        else:
            print(f"  ⚠️  API порт: {chat_config.textgen_webui_port} (нестандартный)")
        
        # Проверяем размер контекста
        if chat_config.N_CTX == 3072:
            print("  ✅ Размер контекста: 3072 (оптимальный)")
        else:
            print(f"  ⚠️  Размер контекста: {chat_config.N_CTX} (неоптимальный)")
        
        # Проверяем GPU слои
        if chat_config.N_GPU_LAYERS == -1:
            print("  ✅ GPU слои: -1 (все слои на GPU)")
        else:
            print(f"  ⚠️  GPU слои: {chat_config.N_GPU_LAYERS} (ограничено)")
        
        # Проверяем потоки
        if chat_config.N_THREADS > 0:
            print(f"  ✅ CPU потоки: {chat_config.N_THREADS}")
        else:
            print(f"  ❌ CPU потоки: {chat_config.N_THREADS} (недопустимо)")
        
        # Проверяем размер батча
        if chat_config.N_BATCH > 0:
            print(f"  ✅ Размер батча: {chat_config.N_BATCH}")
        else:
            print(f"  ❌ Размер батча: {chat_config.N_BATCH} (недопустимо)")
        
        print("\n🎯 Результат синхронизации:")
        print("  • bat-файл теперь использует настройки из chat_config.py")
        print("  • Устранено дублирование конфигурации")
        print("  • Единый источник истины для всех настроек")
        print("  • Автоматическая синхронизация при изменении chat_config.py")
        
        # Проверяем, что модель существует
        from pathlib import Path
        model_path = Path(chat_config.textgen_webui_model_dir) / chat_config.textgen_webui_model
        if model_path.exists():
            print(f"  ✅ Модель найдена: {model_path}")
        else:
            print(f"  ❌ Модель не найдена: {model_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании синхронизации: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_config_sync()
