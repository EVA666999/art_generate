#!/usr/bin/env python3
"""
Основной файл приложения FastAPI для генерации изображений и чат-бота.
"""

import sys
import os
from pathlib import Path

# Добавляем корневую директорию проекта в PYTHONPATH
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Проверяем импорт llama_cpp перед запуском
try:
    import llama_cpp
    print(f"✅ llama_cpp импортирован успешно! Версия: {llama_cpp.__version__}")
except ImportError as e:
    print("❌ Ошибка импорта llama_cpp!")
    print("Это означает, что llama-cpp-python не установлен или установлен неправильно.")
    print("\n🔧 Для автоматической установки выполните:")
    print("   python install_llama_cpp.py")
    print("   или")
    print("   install_llama_cpp.bat (для Windows)")
    print("\n📋 Ручная установка:")
    print("   Для CUDA: pip install llama-cpp-python --force-reinstall --index-url https://jllllll.github.io/llama-cpp-python-cuBLAS-wheels/cu121")
    print("   Для CPU: pip install llama-cpp-python")
    sys.exit(1)
except Exception as e:
    print(f"❌ Неожиданная ошибка при импорте llama_cpp: {e}")
    print("Возможно, проблема с нативными библиотеками.")
    print("Попробуйте переустановить llama-cpp-python:")
    print("   python install_llama_cpp.py")
    sys.exit(1)

from datetime import datetime
import logging

# Добавляем текущую директорию в путь для импорта
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from app.auth import auth, register
from app.routers import generation
from app.config.settings import settings
from app.utils.logger import setup_logger, Logger
from app.config.logger_config import LoggerConfig
from contextlib import asynccontextmanager
import asyncio
from loguru import logger
from fastapi.responses import JSONResponse
import traceback
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from app.chat_bot.api import chat_endpoints, character_endpoints
from app.users.models import users
from app.database.db import engine
from app.config.cuda_config import configure_cuda

# Настраиваем логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация конфигурации логгера
logger_config = LoggerConfig()

# Инициализируем логгер
app_logger = setup_logger(
    bot_token=logger_config.TELEGRAM_BOT_TOKEN or "",
    chat_id=logger_config.TELEGRAM_CHAT_ID or "",
    log_level=logger_config.LOG_LEVEL,
    log_file=logger_config.LOG_FILE,
    log_rotation=logger_config.LOG_ROTATION,
    log_retention=logger_config.LOG_RETENTION
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    app_logger.info("Starting up FastAPI application...")
    try:
        configure_cuda()
        app_logger.info("CUDA успешно инициализирована")
    except Exception as e:
        app_logger.error(f"Ошибка при инициализации CUDA: {str(e)}")
    yield
    app_logger.info("Shutting down FastAPI application...")

app = FastAPI(
    title="Stable Diffusion API",
    description="API для генерации изображений с помощью Stable Diffusion",
    version="1.0.0",
    lifespan=lifespan
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(register.router)
app.include_router(generation.router)
app.include_router(chat_endpoints.router)
app.include_router(character_endpoints.router)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    error_msg = f"Validation error: {exc.errors()}"
    app_logger.error(error_msg)
    
    # Отправляем уведомление в Telegram
    await app_logger.send_log(
        f"Validation Error:\nRequest: {request.url}\nMethod: {request.method}\nErrors: {exc.errors()}"
    )
    
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()}
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # Формируем детальное сообщение об ошибке
    error_msg = f"""
Error occurred at {datetime.now()}
Request: {request.url}
Method: {request.method}
Error Type: {type(exc).__name__}
Error Message: {str(exc)}
Traceback:
{traceback.format_exc()}
"""
    app_logger.error(error_msg)
    
    # Отправляем уведомление в Telegram только если бот включен
    if logger_config.TELEGRAM_BOT_ENABLED:
        try:
            if logger_config.TELEGRAM_BOT_TOKEN and logger_config.TELEGRAM_CHAT_ID:
                for _ in range(logger_config.TELEGRAM_BOT_RETRY_COUNT):
                    try:
                        await app_logger.send_log(
                            f"🚨 <b>Error {type(exc).__name__}</b>\n"
                            f"Request: {request.url}\n"
                            f"Method: {request.method}\n"
                            f"Error: {str(exc)}\n"
                            f"Time: {datetime.now()}"
                        )
                        break
                    except Exception as retry_error:
                        if _ == logger_config.TELEGRAM_BOT_RETRY_COUNT - 1:
                            raise retry_error
                        await asyncio.sleep(1)  # Пауза перед повторной попыткой
        except Exception as e:
            app_logger.error(f"Failed to send Telegram notification: {str(e)}")
    
    # Определяем статус код
    status_code = 500
    if isinstance(exc, HTTPException):
        status_code = exc.status_code
    
    return JSONResponse(
        status_code=status_code,
        content={
            "detail": str(exc),
            "type": type(exc).__name__
        }
    )

@app.get("/")
async def root():
    return {"message": "API is running"}

# Добавляем обработчик для 404 ошибок
@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    error_msg = f"404 Not Found: {request.url}"
    app_logger.error(error_msg)
    
    # Отправляем уведомление в Telegram
    await app_logger.send_log(
        f"404 Not Found:\nRequest: {request.url}\nMethod: {request.method}"
    )
    
    return JSONResponse(
        status_code=404,
        content={
            "detail": f"Not Found: {request.url}",
            "type": "not_found"
        }
    )

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)