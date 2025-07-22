#!/usr/bin/env python3
"""
Скрипт для запуска text-generation-webui
Запускается отдельно от основного FastAPI приложения
"""

import os
import sys
import subprocess
import time
import socket
from pathlib import Path
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_port(port: int, host: str = '127.0.0.1') -> bool:
    """Проверяет, доступен ли порт"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception:
        return False

def main():
    """Основная функция запуска text-generation-webui"""
    
    # Теперь путь всегда к text-generation-webui
    webui_dir = Path(__file__).parent.resolve()
    model_dir = "models/main_model"
    model_name = "Llama-3.1-128k-Dark-Planet-Uncensored-8B-Q4_k_s.gguf"
    api_port = 5000
    listen_port = 7861
    
    logger.info(f"🚀 Запуск text-generation-webui из {webui_dir}")
    
    # Проверяем существование директорий
    model_path = webui_dir / model_dir
    if not model_path.exists():
        logger.error(f"❌ Директория моделей {model_path} не найдена")
        return False
        
    model_file = model_path / model_name
    if not model_file.exists():
        logger.error(f"❌ Модель {model_file} не найдена")
        return False
    
    # Проверяем, не занят ли порт
    if check_port(api_port):
        logger.warning(f"⚠️ Порт {api_port} уже занят. Возможно, text-generation-webui уже запущен.")
        return True
    
    # Команда для запуска
    cmd = [
        sys.executable,  # Текущий Python
        "server.py",
        "--api",
        "--api-port", str(api_port),
        "--listen",
        "--listen-port", str(listen_port),
        "--model", model_name,
        "--loader", "llama.cpp",
        "--model-dir", model_dir
    ]
    
    logger.info(f"📁 Рабочая директория: {webui_dir}")
    logger.info(f"🤖 Модель: {model_name}")
    logger.info(f"🔌 API порт: {api_port}")
    logger.info(f"🌐 Web порт: {listen_port}")
    logger.info(f"⚡ Команда: {' '.join(cmd)}")
    
    try:
        # Запускаем процесс
        logger.info("🔄 Запускаем text-generation-webui...")
        process = subprocess.Popen(
            cmd,
            cwd=webui_dir
        )
        
        # Ждем запуска и выводим логи
        logger.info("⏳ Ожидаем загрузки модели...")
        for i in range(60):  # 60 секунд максимум
            # Проверяем, не завершился ли процесс
            if process.poll() is not None:
                logger.error("❌ text-generation-webui завершился с ошибкой")
                return False
            
            # Проверяем порт
            if check_port(api_port):
                logger.info("✅ text-generation-webui успешно запущен!")
                logger.info(f"📚 API: http://localhost:{api_port}")
                logger.info(f"🌐 Web: http://localhost:{listen_port}")
                logger.info("🔄 Сервер работает. Для остановки используйте Ctrl+C.")
                process.wait()
                return True
            
            if i % 5 == 0:
                logger.info(f"⏳ Ожидаем... ({i+1}/60)")
            
            time.sleep(1)
        
        logger.error("❌ text-generation-webui не запустился за 60 секунд")
        process.terminate()
        return False
        
    except Exception as e:
        logger.error(f"❌ Ошибка запуска: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1) 