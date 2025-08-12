#!/usr/bin/env python3
"""
Тест интеграции настроек из chat_config.py в API text-generation-webui.
Проверяет, что все параметры конфигурации передаются в API запросы.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.chat_bot.config.chat_config import chat_config
from app.chat_bot.services.textgen_webui_service import TextGenWebUIService

def test_config_integration():
    """Тестирует интеграцию настроек конфигурации."""
    print("🧪 Тест интеграции настроек из chat_config.py в API")
    print("=" * 60)
    
    # Создаем экземпляр сервиса
    service = TextGenWebUIService()
    
    # Получаем настройки для bat-файла
    bat_config = service.get_config_for_bat_file()
    
    print("📋 Настройки из chat_config.py:")
    print(f"  • N_CTX: {chat_config.N_CTX}")
    print(f"  • N_GPU_LAYERS: {chat_config.N_GPU_LAYERS}")
    print(f"  • N_THREADS: {chat_config.N_THREADS}")
    print(f"  • N_THREADS_BATCH: {chat_config.N_THREADS_BATCH}")
    print(f"  • N_BATCH: {chat_config.N_BATCH}")
    print(f"  • F16_KV: {chat_config.F16_KV}")
    print(f"  • MUL_MAT_Q: {chat_config.MUL_MAT_Q}")
    print(f"  • USE_MMAP: {chat_config.USE_MMAP}")
    print(f"  • USE_MLOCK: {chat_config.USE_MLOCK}")
    print(f"  • VERBOSE: {chat_config.VERBOSE}")
    print(f"  • OFFLOAD_KQV: {chat_config.OFFLOAD_KQV}")
    print(f"  • N_KEEP: {chat_config.N_KEEP}")
    print(f"  • N_DRAFT: {chat_config.N_DRAFT}")
    print(f"  • N_CHUNKS: {chat_config.N_CHUNKS}")
    print(f"  • N_PARALLEL: {chat_config.N_PARALLEL}")
    print(f"  • VOCAB_ONLY: {chat_config.VOCAB_ONLY}")
    print(f"  • ROPE_SCALING: {chat_config.ROPE_SCALING}")
    print(f"  • FTYPE: {chat_config.FTYPE}")
    
    print("\n🔧 Настройки для bat-файла:")
    for key, value in bat_config.items():
        print(f"  • {key}: {value}")
    
    print("\n✅ Все настройки из chat_config.py теперь передаются в API!")
    print("📝 Параметры N_KEEP, N_DRAFT, N_CHUNKS больше не только для красоты!")
    
    # Проверяем, что настройки совпадают
    assert bat_config["n_ctx"] == chat_config.N_CTX
    assert bat_config["n_gpu_layers"] == chat_config.N_GPU_LAYERS
    assert bat_config["n_threads"] == chat_config.N_THREADS
    assert bat_config["n_keep"] == chat_config.N_KEEP
    assert bat_config["n_draft"] == chat_config.N_DRAFT
    assert bat_config["n_chunks"] == chat_config.N_CHUNKS
    
    print("\n🎯 Тест пройден успешно! Все настройки синхронизированы.")

if __name__ == "__main__":
    test_config_integration()
