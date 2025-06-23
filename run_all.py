"""
Скрипт для запуска API и бота одновременно.
"""
import subprocess
import sys
import os
from pathlib import Path

def run_api():
    """Запуск FastAPI приложения."""
    api_process = subprocess.Popen(
        [sys.executable, "app/main.py"],
        env=os.environ.copy()
    )
    return api_process

def run_bot():
    """Запуск Telegram бота."""
    bot_process = subprocess.Popen(
        [sys.executable, "telegram_monitor_bot/src/bot.py"],
        env=os.environ.copy()
    )
    return bot_process

def main():
    """Основная функция запуска."""
    try:
        # Устанавливаем пакет в режиме разработки
        subprocess.run([sys.executable, "-m", "pip", "install", "-e", "."], check=True)
        
        # Запускаем API
        api_process = run_api()
        print("API запущен...")
        
        # Запускаем бота
        bot_process = run_bot()
        print("Бот запущен...")
        
        # Ждем завершения процессов
        api_process.wait()
        bot_process.wait()
        
    except KeyboardInterrupt:
        print("\nЗавершение работы...")
        api_process.terminate()
        bot_process.terminate()
    except Exception as e:
        print(f"Ошибка: {e}")
        if 'api_process' in locals():
            api_process.terminate()
        if 'bot_process' in locals():
            bot_process.terminate()
        sys.exit(1)

if __name__ == "__main__":
    main() 