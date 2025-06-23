"""
Конфигурация путей приложения
"""
import os
from pathlib import Path

# Базовые пути
BASE_DIR = Path(__file__).parent.parent.parent
APP_DIR = BASE_DIR / "app"
DATA_DIR = APP_DIR / "data"
LOGS_DIR = APP_DIR / "logs"
IMAGES_DIR = APP_DIR / "images"

# Создаем директории, если они не существуют
for directory in [DATA_DIR, LOGS_DIR, IMAGES_DIR]:
    directory.mkdir(exist_ok=True)

# Пути к файлам
LOGS_PATH = LOGS_DIR
IMAGES_PATH = IMAGES_DIR
DATA_PATH = DATA_DIR

# Получаем путь к корню проекта
PROJECT_ROOT = Path(__file__).parent.parent

# Базовый путь для сохранения изображений
IMAGES_DIR = os.getenv("IMAGES_DIR", "images")

# Полный путь к директории с изображениями
IMAGES_PATH = (PROJECT_ROOT / IMAGES_DIR).absolute()

# Создаем директорию, если она не существует
IMAGES_PATH.mkdir(parents=True, exist_ok=True)

# Путь для временных файлов
TEMP_DIR = os.getenv("TEMP_DIR", "temp")
TEMP_PATH = (PROJECT_ROOT / TEMP_DIR).absolute()
TEMP_PATH.mkdir(parents=True, exist_ok=True) 