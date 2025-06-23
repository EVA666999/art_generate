"""
Скрипт для одновременного запуска бота и основного приложения
"""
import multiprocessing
import subprocess
import sys
from pathlib import Path

def run_bot():
    """Запуск телеграм бота"""
    bot_path = Path(__file__).parent / "src" / "bot.py"
    # Используем Python из виртуального окружения бота
    python_path = Path(__file__).parent / "venv" / "Scripts" / "python.exe"
    subprocess.run([str(python_path), str(bot_path)])

def run_main():
    """Запуск основного приложения"""
    main_path = Path(__file__).parent.parent / "app" / "main.py"
    # Используем Python из основного виртуального окружения
    python_path = Path(__file__).parent.parent / ".venv" / "Scripts" / "python.exe"
    subprocess.run([str(python_path), str(main_path)])

if __name__ == "__main__":
    # Создаем процессы
    bot_process = multiprocessing.Process(target=run_bot)
    main_process = multiprocessing.Process(target=run_main)
    
    try:
        # Запускаем оба процесса
        print("Запуск бота...")
        bot_process.start()
        print("Запуск основного приложения...")
        main_process.start()
        
        # Ждем завершения процессов
        bot_process.join()
        main_process.join()
        
    except KeyboardInterrupt:
        print("\nЗавершение работы...")
        bot_process.terminate()
        main_process.terminate()
        bot_process.join()
        main_process.join() 