import logging
import os
from datetime import datetime

# Создаем директорию для логов, если её нет
log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
os.makedirs(log_dir, exist_ok=True)

# Настройка форматирования логов
log_format = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Создаем файловый обработчик
log_file = os.path.join(log_dir, f"generation_{datetime.now().strftime('%Y%m%d')}.log")
file_handler = logging.FileHandler(log_file, encoding='utf-8')
file_handler.setFormatter(log_format)

# Создаем консольный обработчик
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_format)

# Настраиваем корневой логгер
logger = logging.getLogger("generation")
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)
logger.addHandler(console_handler) 