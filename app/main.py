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
from app.database.db import async_session_maker
from app.chat_bot.create.character_service import character_service

# Настраиваем логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# text-generation-webui теперь запускается отдельно

async def sync_characters_to_db():
    """Добавляет новых персонажей из character_service в БД, если их нет."""
    from app.chat_bot.models.models import CharacterDB
    from sqlalchemy import select
    
    logger.info(f"🔄 Начинаем синхронизацию {len(character_service.characters)} персонажей...")
    
    async with async_session_maker() as db:
        logger.info("✅ Подключение к БД установлено")
        
        for char_name, char in character_service.characters.items():
            logger.info(f"🔍 Проверяем персонажа: {char_name}")
            
            try:
                result = await db.execute(select(CharacterDB).where(CharacterDB.name == char.name))
                db_char = result.scalar_one_or_none()
                
                if not db_char:
                    logger.info(f"➕ Добавляем персонажа в БД: {char.name}")
                    await character_service.add_to_db(char, db)
                    logger.info(f"✅ Персонаж {char.name} успешно добавлен в БД")
                else:
                    logger.info(f"ℹ️ Персонаж {char.name} уже есть в БД (ID: {db_char.id})")
                    
            except Exception as e:
                logger.error(f"❌ Ошибка при обработке персонажа {char_name}: {e}")
                logger.error(f"Тип ошибки: {type(e).__name__}")
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")
        
        logger.info("✅ Синхронизация персонажей завершена")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    logger.info("🚀 Запуск приложения...")
    logger.info("📋 Проверяем доступность character_service...")
    
    try:
        logger.info(f"✅ character_service доступен, персонажей: {len(character_service.characters)}")
        for char_name in character_service.characters.keys():
            logger.info(f"   - {char_name}")
    except Exception as e:
        logger.error(f"❌ Ошибка при проверке character_service: {e}")
    
    # text-generation-webui запускается отдельно
    logger.info("ℹ️ text-generation-webui должен быть запущен отдельно")
    
    # Синхронизируем персонажей
    logger.info("🔄 Начинаем синхронизацию персонажей...")
    try:
        await sync_characters_to_db()
        logger.info("✅ Синхронизация персонажей завершена успешно")
    except Exception as e:
        logger.error(f"❌ Ошибка при синхронизации персонажей: {e}")
        logger.error(f"Тип ошибки: {type(e).__name__}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
    
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

@app.on_event("startup")
async def startup_event():
    """Дополнительное событие запуска для синхронизации персонажей."""
    logger.info("🔄 Событие startup: начинаем синхронизацию персонажей...")
    try:
        await sync_characters_to_db()
        logger.info("✅ Событие startup: синхронизация персонажей завершена")
    except Exception as e:
        logger.error(f"❌ Событие startup: ошибка синхронизации персонажей: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")

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
    from routers.generation import router as generation_router
    app.include_router(generation_router)
    logger.info("✓ Роутер generation подключен")
except Exception as e:
    logger.error(f"✗ Ошибка подключения роутера generation: {e}")
    logger.error(f"Тип ошибки: {type(e).__name__}")
    import traceback
    logger.error(f"Traceback: {traceback.format_exc()}")

try:
    from chat_bot.api import chat_router, character_router
    app.include_router(chat_router)
    app.include_router(character_router)
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
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/api/characters/")
async def legacy_characters_redirect(request: Request):
    """Legacy endpoint для совместимости с фронтендом."""
    try:
        from app.chat_bot.create.character_service import character_service
        characters = character_service.list_characters()
        logger.info(f"Загружено персонажей: {len(characters)}")
        return characters
    except Exception as e:
        logger.error(f"Ошибка загрузки персонажей: {e}")
        return []

@app.post("/api/chat/")
async def legacy_chat_redirect(request: Request):
    return RedirectResponse(url="/api/v1/chat/")

if __name__ == "__main__":
    logger.info("Запуск основного приложения...")
    uvicorn.run(app, host="0.0.0.0", port=8000)