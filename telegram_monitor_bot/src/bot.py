"""
Основной модуль телеграм бота для мониторинга.
"""
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram.error import TimedOut, NetworkError
from telegram.request import HTTPXRequest
from loguru import logger
from app.utils.logger import setup_logger, log_exceptions
from app.config.logger_config import LoggerConfig

# Загружаем конфигурацию
config = LoggerConfig()

# Проверяем наличие необходимых настроек
if not config.TELEGRAM_BOT_TOKEN or not config.TELEGRAM_CHAT_ID:
    logger.error("Отсутствуют необходимые настройки Telegram (TELEGRAM_BOT_TOKEN или TELEGRAM_CHAT_ID)")
    raise ValueError("Необходимо указать TELEGRAM_BOT_TOKEN и TELEGRAM_CHAT_ID в .env файле")

# Настраиваем логгер
setup_logger(
    bot_token=config.TELEGRAM_BOT_TOKEN,
    chat_id=config.TELEGRAM_CHAT_ID,
    log_file="logs/telegram_bot.log"
)

# Настройки HTTP клиента
REQUEST_TIMEOUT = 30.0  # секунды
CONNECT_TIMEOUT = 10.0  # секунды
READ_TIMEOUT = 30.0     # секунды
WRITE_TIMEOUT = 30.0    # секунды
POOL_TIMEOUT = 30.0     # секунды

@log_exceptions
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start."""
    try:
        await update.message.reply_text(
            "👋 Привет! Я бот для мониторинга генерации изображений.\n"
            "Я буду отправлять вам уведомления об ошибках и важных событиях."
        )
        logger.info(f"Пользователь {update.effective_user.id} запустил бота")
    except (TimedOut, NetworkError) as e:
        logger.error(f"Сетевая ошибка при обработке команды start: {str(e)}")
        # Повторная попытка
        try:
            await update.message.reply_text("Повторная попытка...")
        except Exception as retry_error:
            logger.error(f"Ошибка при повторной попытке: {str(retry_error)}")
    except Exception as e:
        logger.error(f"Ошибка при обработке команды start: {str(e)}")
        raise

@log_exceptions
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /help."""
    try:
        help_text = (
            "🤖 Доступные команды:\n"
            "/start - Начать работу с ботом\n"
            "/help - Показать это сообщение\n"
            "/status - Проверить статус генерации"
        )
        await update.message.reply_text(help_text)
        logger.info(f"Пользователь {update.effective_user.id} запросил помощь")
    except (TimedOut, NetworkError) as e:
        logger.error(f"Сетевая ошибка при обработке команды help: {str(e)}")
        # Повторная попытка
        try:
            await update.message.reply_text("Повторная попытка...")
        except Exception as retry_error:
            logger.error(f"Ошибка при повторной попытке: {str(retry_error)}")
    except Exception as e:
        logger.error(f"Ошибка при обработке команды help: {str(e)}")
        raise

@log_exceptions
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /status."""
    try:
        # Здесь будет логика проверки статуса
        await update.message.reply_text("✅ Система работает нормально")
        logger.info(f"Пользователь {update.effective_user.id} запросил статус")
    except (TimedOut, NetworkError) as e:
        logger.error(f"Сетевая ошибка при проверке статуса: {str(e)}")
        # Повторная попытка
        try:
            await update.message.reply_text("Повторная попытка...")
        except Exception as retry_error:
            logger.error(f"Ошибка при повторной попытке: {str(retry_error)}")
    except Exception as e:
        logger.error(f"Ошибка при проверке статуса: {str(e)}")
        raise

def main() -> None:
    """Запуск бота."""
    try:
        # Создаем HTTP клиент с настройками таймаутов
        request = HTTPXRequest(
            connection_pool_size=8,
            read_timeout=READ_TIMEOUT,
            write_timeout=WRITE_TIMEOUT,
            connect_timeout=CONNECT_TIMEOUT,
            pool_timeout=POOL_TIMEOUT
        )

        # Создаем приложение с настроенным HTTP клиентом
        application = (
            Application.builder()
            .token(config.TELEGRAM_BOT_TOKEN)
            .request(request)
            .build()
        )

        # Добавляем обработчики команд
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("status", status))

        # Запускаем бота
        application.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True,
            timeout=REQUEST_TIMEOUT
        )
        logger.info("Бот успешно запущен")
    except Exception as e:
        logger.critical(f"Критическая ошибка при запуске бота: {str(e)}")
        raise

if __name__ == "__main__":
    main()