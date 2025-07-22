#!/usr/bin/env python3
"""
Скрипт для запуска сервера с правильными путями.
Работает независимо от того, откуда запускается.
"""
import sys
import os
from pathlib import Path

# Определяем корневую директорию проекта
project_root = Path(__file__).parent
app_dir = project_root / "app"

# Добавляем пути в sys.path
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(app_dir))

# Устанавливаем рабочую директорию
os.chdir(str(project_root))

print(f"🚀 Запуск сервера...")
print(f"📁 Рабочая директория: {os.getcwd()}")
print(f"📦 Python path: {sys.path[:3]}")

# Импортируем и запускаем main
if __name__ == "__main__":
    try:
        from app.main import app
        import uvicorn
        
        print("✅ Сервер успешно импортирован")
        print("🌐 Запускаем на http://localhost:8000")
        
        uvicorn.run(app, host="0.0.0.0", port=8000)
        
    except Exception as e:
        print(f"❌ Ошибка запуска сервера: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 