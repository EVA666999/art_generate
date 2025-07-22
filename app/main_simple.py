#!/usr/bin/env python3
"""
Упрощенная версия основного файла приложения FastAPI для тестирования.
"""

import sys
import os
from pathlib import Path
from datetime import datetime
import logging
import traceback

# Добавляем корневую директорию проекта в PYTHONPATH
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import uvicorn
from loguru import logger

# Настраиваем логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Создаем простое приложение без сложной инициализации
app = FastAPI(
    title="Stable Diffusion API (Simple)",
    description="Упрощенная версия API для генерации изображений",
    version="1.0.0",
    docs_url="/docs_app",
    redoc_url="/redoc"
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем только базовые роутеры
try:
    from app.routers import generation
    app.include_router(generation.router)
    logger.info("✓ Роутер generation подключен")
except Exception as e:
    logger.error(f"✗ Ошибка подключения роутера generation: {e}")

try:
    from app.auth import auth, register
    app.include_router(auth.router)
    app.include_router(register.router)
    logger.info("✓ Роутеры auth и register подключены")
except Exception as e:
    logger.error(f"✗ Ошибка подключения роутеров auth/register: {e}")

# Подключаем роутеры чата
try:
    from app.chat_bot.api import chat_endpoints
    app.include_router(chat_endpoints.router)
    logger.info("✓ Роутер чата подключен")
except Exception as e:
    logger.error(f"✗ Ошибка подключения роутера чата: {e}")

# Подключаем статические файлы
try:
    from fastapi.staticfiles import StaticFiles
    app.mount("/static", StaticFiles(directory="app/static"), name="static")
    logger.info("✓ Статические файлы подключены")
except Exception as e:
    logger.error(f"✗ Ошибка подключения статических файлов: {e}")

# Простые обработчики ошибок
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
):
    error_msg = f"Validation error: {exc.errors()}"
    logger.error(error_msg)
    
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()}
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    error_msg = f"""
Error occurred at {datetime.now()}
Request: {request.url}
Method: {request.method}
Error Type: {type(exc).__name__}
Error Message: {str(exc)}
Traceback:
{traceback.format_exc()}
"""
    logger.error(error_msg)
    
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
    return {"message": "Simple API is running"}

@app.get("/chat")
async def chat_interface():
    """Отображает чат-интерфейс"""
    from fastapi.responses import FileResponse
    return FileResponse("app/static/chat.html")

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    logger.info("Запуск упрощенной версии приложения...")
    uvicorn.run(app, host="0.0.0.0", port=8000) 