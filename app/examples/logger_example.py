"""
Пример использования логгера.
"""
import asyncio
from app.utils.logger import setup_logger, log_exceptions
from app.config.logger_config import LoggerConfig
from loguru import logger

# Загружаем конфигурацию (нужны только TELEGRAM_BOT_TOKEN и TELEGRAM_CHAT_ID)
config = LoggerConfig()

# Настраиваем логгер (LOG_LEVEL уже установлен как ERROR в конфигурации)
setup_logger(
    bot_token=config.TELEGRAM_BOT_TOKEN,
    chat_id=config.TELEGRAM_CHAT_ID,
    log_file=config.LOG_FILE
)

@log_exceptions
async def example_function():
    """Пример функции с логированием."""
    # Эти сообщения НЕ будут отправлены в Telegram (уровень ниже ERROR)
    logger.debug("Отладочная информация")
    logger.info("Информационное сообщение")
    logger.warning("Предупреждение")
    
    # Эти сообщения БУДУТ отправлены в Telegram
    try:
        1/0
    except Exception as e:
        logger.error(f"Произошла ошибка: {str(e)}")
        raise

async def main():
    """Основная функция."""
    try:
        await example_function()
    except Exception as e:
        logger.critical(f"Критическая ошибка в main: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main()) 