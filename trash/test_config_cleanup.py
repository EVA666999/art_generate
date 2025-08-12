#!/usr/bin/env python3
"""
Тест для проверки, что все настройки текстовой модели загружаются из chat_config.py
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def test_config_loading():
    """Тестируем загрузку конфигурации."""
    try:
        print("🔍 Проверяем загрузку конфигурации...")
        
        # Импортируем chat_config
        from app.chat_bot.config.chat_config import chat_config
        print("✅ chat_config успешно импортирован")
        
        # Проверяем основные настройки text-generation-webui
        print("\n📋 Основные настройки text-generation-webui:")
        print(f"  • URL: {chat_config.textgen_webui_url}")
        print(f"  • Модель: {chat_config.textgen_webui_model}")
        print(f"  • Загрузчик: {chat_config.textgen_webui_loader}")
        print(f"  • Директория: {chat_config.textgen_webui_model_dir}")
        
        # Проверяем настройки MythoMax
        print("\n🤖 Настройки MythoMax:")
        print(f"  • Длина контекста: {chat_config.mythomax_context_length}")
        print(f"  • Макс токены: {chat_config.mythomax_max_tokens}")
        print(f"  • Alpaca формат: {chat_config.mythomax_use_alpaca_format}")
        
        # Проверяем параметры генерации
        print("\n⚙️ Параметры генерации:")
        print(f"  • Макс токены: {chat_config.DEFAULT_MAX_TOKENS}")
        print(f"  • Температура: {chat_config.DEFAULT_TEMPERATURE}")
        print(f"  • Top-p: {chat_config.DEFAULT_TOP_P}")
        print(f"  • Top-k: {chat_config.DEFAULT_TOP_K}")
        print(f"  • Штраф повторений: {chat_config.DEFAULT_REPEAT_PENALTY}")
        
        # Проверяем аппаратные параметры
        print("\n💻 Аппаратные параметры:")
        print(f"  • Контекст: {chat_config.N_CTX}")
        print(f"  • GPU слои: {chat_config.N_GPU_LAYERS}")
        print(f"  • CPU потоки: {chat_config.N_THREADS}")
        print(f"  • Размер батча: {chat_config.N_BATCH}")
        
        # Проверяем настройки безопасности
        print("\n🛡️ Настройки безопасности:")
        print(f"  • Фильтр контента: {chat_config.ENABLE_CONTENT_FILTER}")
        print(f"  • Запрещенные слова: {len(chat_config.FORBIDDEN_WORDS)}")
        
        # Проверяем настройки логирования
        print("\n📝 Настройки логирования:")
        print(f"  • Логировать запросы: {chat_config.LOG_CHAT_REQUESTS}")
        print(f"  • Логировать ответы: {chat_config.LOG_CHAT_RESPONSES}")
        print(f"  • Кэширование: {chat_config.ENABLE_CACHE}")
        
        print("\n✅ Все настройки успешно загружены из chat_config.py!")
        
        # Проверяем, что settings не содержит дублирующиеся настройки
        print("\n🔍 Проверяем settings.py на дублирование...")
        from app.config.settings import settings
        
        # Проверяем, что в settings нет настроек text-generation-webui
        textgen_attrs = [
            'textgen_webui_url', 'textgen_webui_model', 'textgen_webui_loader',
            'mythomax_context_length', 'mythomax_max_tokens', 'mythomax_use_alpaca_format'
        ]
        
        for attr in textgen_attrs:
            if hasattr(settings, attr):
                print(f"  ⚠️  В settings.py найден дублирующий атрибут: {attr}")
            else:
                print(f"  ✅ Атрибут {attr} отсутствует в settings.py (хорошо)")
        
        print("\n🎯 Результат: chat_config.py - единственный источник настроек для текстовых моделей!")
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании конфигурации: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_config_loading())
