#!/usr/bin/env python3
"""
Основной файл приложения FastAPI для генерации изображений и чат-бота.
"""

import sys
from pathlib import Path
from datetime import datetime
import logging
import traceback
from contextlib import asynccontextmanager

# Устанавливаем рабочую директорию ПЕРЕД импортами
import os
project_root = Path(__file__).parent.parent
os.chdir(str(project_root))

# Добавляем корневую директорию проекта в PYTHONPATH
app_root = Path(__file__).parent

# Добавляем оба пути для надежности
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(app_root))

# Проверяем и исправляем импорты
try:
    import pydantic
    print(f"✅ Pydantic version: {pydantic.__version__}")
except ImportError as e:
    print(f"❌ Pydantic import error: {e}")
    sys.exit(1)

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse, RedirectResponse
from fastapi.exceptions import RequestValidationError
import uvicorn
from loguru import logger
# Настраиваем логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



async def sync_characters_to_db():
    """Синхронизация персонажей теперь не нужна - используем character_importer."""
    logger.info("ℹ️ Синхронизация персонажей отключена - используйте character_importer")
    logger.info("📝 Для обновления персонажей используйте: python update_character.py")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    logger.info("🚀 Запуск приложения...")
    

    
    # Синхронизация персонажей отключена - используем character_importer
    logger.info("ℹ️ Синхронизация персонажей отключена - используйте character_importer")
    
    logger.info("🎉 Приложение готово к работе!")
    yield
    
    # Завершение работы приложения
    logger.info("🛑 Останавливаем приложение...")
    logger.info("✅ Приложение остановлено")

# Создаем приложение с lifespan
app = FastAPI(
    title="Stable Diffusion API",
    description="API для генерации изображений с помощью Stable Diffusion",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Событие startup удалено - синхронизация персонажей отключена

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роутеры
try:
    from app.auth import auth, register
    app.include_router(auth.router)
    app.include_router(register.router)
    logger.info("✓ Роутеры auth и register подключены")
except Exception as e:
    logger.error(f"✗ Ошибка подключения роутеров auth/register: {e}")

try:
    from app.routers.generation import router as generation_router
    app.include_router(generation_router)
    logger.info("✓ Роутер generation подключен")
except Exception as e:
    logger.error(f"✗ Ошибка подключения роутера generation: {e}")
    logger.error(f"Тип ошибки: {type(e).__name__}")
    import traceback
    logger.error(f"Traceback: {traceback.format_exc()}")

try:
    logger.info("🔄 Импортируем chat_router...")
    from app.chat_bot.api.chat_endpoints import router as chat_router
    logger.info("✅ chat_router импортирован успешно")
    
    logger.info("🔄 Импортируем character_router...")
    from app.chat_bot.api.character_endpoints import router as character_router
    logger.info("✅ character_router импортирован успешно")
    
    logger.info("🔄 Подключаем chat_router...")
    app.include_router(chat_router)
    logger.info("✅ chat_router подключен")
    
    logger.info("🔄 Подключаем character_router...")
    app.include_router(character_router)
    logger.info("✅ character_router подключен")
    
    logger.info("✓ Роутеры chat и character подключены")
except Exception as e:
    logger.error(f"✗ Ошибка подключения роутеров chat/character: {e}")
    logger.error(f"Тип ошибки: {type(e).__name__}")
    import traceback
    logger.error(f"Traceback: {traceback.format_exc()}")

# Обработчики ошибок
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
    return {"message": "API is running"}

@app.get("/docs_app")
async def docs_app():
    """Перенаправление на документацию."""
    return RedirectResponse(url="/docs")

@app.get("/chat")
async def chat_page():
    """Страница чата."""
    file_path = Path(__file__).parent / "static" / "chat.html"
    return FileResponse(str(file_path))

@app.get("/health")
async def health():
    """Проверка здоровья основного приложения."""
    try:
        # Общий статус приложения
        app_status = {
            "app": "Stable Diffusion API",
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
            "services": {}
        }
        
        return app_status
        
    except Exception as e:
        logger.error(f"Ошибка проверки здоровья приложения: {e}")
        return {
            "app": "Stable Diffusion API",
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.get("/api/v1/characters/")
async def fallback_characters():
    """Fallback endpoint для персонажей если основной API недоступен."""
    try:
        from app.chat_bot.utils.character_importer import character_importer
        from app.database.db import async_session_maker
        from app.chat_bot.models.models import CharacterDB
        from sqlalchemy import select
        
        async with async_session_maker() as db:
            result = await db.execute(
                select(CharacterDB).order_by(CharacterDB.name)
            )
            characters = result.scalars().all()
            
            # Преобразуем в формат, ожидаемый фронтендом (новая схема Alpaca)
            character_list = []
            for char in characters:
                character_list.append({
                    "id": char.id,
                    "name": char.name,
                    "instructions": char.instructions,
                    "system_prompt": char.system_prompt,
                    "response_format": char.response_format,
                    "character_type": getattr(char, 'character_type', 'general'),
                    "rating": getattr(char, 'rating', 'general'),
                    "language": getattr(char, 'language', 'en'),
                    "version": getattr(char, 'version', '1.0')
                })
            
            logger.info(f"Загружено персонажей: {len(character_list)}")
            return character_list
    except Exception as e:
        logger.error(f"Ошибка загрузки персонажей: {e}")
        # Возвращаем пустой список вместо ошибки
        return []

@app.get("/api/characters/")
async def legacy_characters_redirect(request: Request):
    """Legacy endpoint для совместимости с фронтендом."""
    try:
        from app.chat_bot.utils.character_importer import character_importer
        from app.database.db import async_session_maker
        from app.chat_bot.models.models import CharacterDB
        from sqlalchemy import select
        
        async with async_session_maker() as db:
            result = await db.execute(
                select(CharacterDB).order_by(CharacterDB.name)
            )
            characters = result.scalars().all()
            
            # Преобразуем в формат, ожидаемый фронтендом (новая схема Alpaca)
            character_list = []
            for char in characters:
                character_list.append({
                    "id": char.id,
                    "name": char.name,
                    "instructions": char.instructions,
                    "system_prompt": char.system_prompt,
                    "response_format": char.response_format,
                    "character_type": getattr(char, 'character_type', 'general'),
                    "rating": getattr(char, 'rating', 'general'),
                    "language": getattr(char, 'language', 'en'),
                    "version": getattr(char, 'version', '1.0')
                })
            
            logger.info(f"Загружено персонажей: {len(character_list)}")
            return character_list
    except Exception as e:
        logger.error(f"Ошибка загрузки персонажей: {e}")
        return []

@app.post("/api/chat/")
async def legacy_chat_redirect(request: Request):
    return RedirectResponse(url="/api/v1/chat/")

if __name__ == "__main__":
    logger.info("Запуск основного приложения...")
    uvicorn.run(app, host="0.0.0.0", port=8000)