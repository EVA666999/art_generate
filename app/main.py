#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Основной файл приложения FastAPI для генерации изображений и чат-бота.
"""

import sys
from pathlib import Path
from datetime import datetime
import logging
import traceback
import asyncio
from contextlib import asynccontextmanager

# Устанавливаем правильную кодировку для работы с Unicode
import locale
import os
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Настройка кодировки для Windows
if sys.platform == "win32":
    import codecs
    # Устанавливаем UTF-8 как кодировку по умолчанию
    try:
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    except:
        try:
            locale.setlocale(locale.LC_ALL, 'C.UTF-8')
        except:
            pass
    
    # Устанавливаем переменные окружения для правильной кодировки
    os.environ['LC_ALL'] = 'en_US.UTF-8'
    os.environ['LANG'] = 'en_US.UTF-8'
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    
    # Устанавливаем кодировку по умолчанию для всех операций
    import locale
    locale.getpreferredencoding = lambda: 'utf-8'
    
    # НЕ перенаправляем stdout и stderr, чтобы не конфликтовать с логированием
    # sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
    # sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())

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
    print(f"[OK] Pydantic version: {pydantic.__version__}")
except ImportError as e:
    print(f"[ERROR] Pydantic import error: {e}")
    sys.exit(1)

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from fastapi.responses import JSONResponse, FileResponse, RedirectResponse, StreamingResponse
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
import uvicorn
from pydantic import BaseModel
from typing import Optional

# Импорты для генерации изображений
from app.chat_bot.add_character import get_character_data
from app.services.face_refinement import FaceRefinementService
from app.schemas.generation import GenerationSettings
from app.config.settings import settings

# Импорты моделей для Alembic
from app.models.chat_history import ChatHistory

# Схема для запроса генерации изображений
class ImageGenerationRequest(BaseModel):
    prompt: str
    negative_prompt: Optional[str] = None
    use_default_prompts: bool = True
    seed: Optional[int] = None
    steps: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    cfg_scale: Optional[float] = None
    sampler_name: Optional[str] = None
    character: Optional[str] = None
    user_id: Optional[int] = None  # ID пользователя для проверки подписки

# Создаем папку для логов, если её нет
os.makedirs('logs', exist_ok=True)

# Настраиваем логирование с правильной кодировкой
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('logs/app.log', encoding='utf-8')
    ],
    force=True  # Принудительно перезаписываем конфигурацию
)
logger = logging.getLogger(__name__)



async def sync_characters_to_db():
    """Синхронизация персонажей теперь не нужна - используем character_importer."""
    logger.info("[INFO] Синхронизация персонажей отключена - используйте character_importer")
    logger.info("[NOTE] Для обновления персонажей используйте: python update_character.py")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    logger.info("[START] Запуск приложения...")
    
    # Логируем информацию о модели при запуске
    try:
        import sys
        from pathlib import Path
        webui_path = Path(__file__).parent.parent / "stable-diffusion-webui"
        sys.path.insert(0, str(webui_path))
        from model_config import get_model_info, check_model_files
        model_info = get_model_info()
        model_available = check_model_files()
        
        if model_info and model_available:
            logger.info(f"[TARGET] Загружена модель: {model_info['name']} ({model_info['size_mb']} MB)")
            if model_info["vae_name"]:
                logger.info(f"[ART] VAE: {model_info['vae_name']}")
            else:
                logger.info("[ART] VAE: Встроенный")
        else:
            logger.warning("[WARNING] Модель не найдена или недоступна")
    except Exception as e:
        logger.warning(f"[WARNING] Не удалось получить информацию о модели: {e}")
    
    # Синхронизация персонажей отключена - используем character_importer
    logger.info("[INFO] Синхронизация персонажей отключена - используйте character_importer")
    
    logger.info("🎉 Приложение готово к работе!")
    yield
    
    # Завершение работы приложения
    logger.info("🛑 Останавливаем приложение...")
    logger.info("[OK] Приложение остановлено")

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

# Middleware для правильной обработки Unicode
@app.middleware("http")
async def unicode_middleware(request: Request, call_next):
    """Middleware для правильной обработки Unicode в запросах."""
    try:
        # Логируем все запросы для отладки
        logger.info(f"Request: {request.method} {request.url}")
        
        # Устанавливаем правильную кодировку для запроса
        if hasattr(request, '_body'):
            # Если есть тело запроса, убеждаемся что оно правильно декодировано
            pass
        
        response = await call_next(request)
        logger.info(f"Response: {response.status_code}")
        return response
    except UnicodeError as e:
        logger.error(f"Unicode error in middleware: {e}")
        return JSONResponse(
            status_code=400,
            content={"detail": f"Unicode processing error: {str(e)}"}
        )
    except Exception as e:
        logger.error(f"Error in middleware: {e}")
        return JSONResponse(
            status_code=500,
            content={"detail": f"Internal server error: {str(e)}"}
        )

# Настройка сессий для OAuth
app.add_middleware(SessionMiddleware, secret_key="your-secret-key-change-in-production")

# Обработчик ошибок для Unicode
@app.exception_handler(UnicodeEncodeError)
async def unicode_encode_handler(request: Request, exc: UnicodeEncodeError):
    """Обработчик ошибок кодировки Unicode."""
    logger.error(f"Unicode encoding error: {exc}")
    return JSONResponse(
        status_code=400,
        content={"detail": f"Unicode encoding error: {str(exc)}"}
    )

@app.exception_handler(UnicodeDecodeError)
async def unicode_decode_handler(request: Request, exc: UnicodeDecodeError):
    """Обработчик ошибок декодировки Unicode."""
    logger.error(f"Unicode decoding error: {exc}")
    return JSONResponse(
        status_code=400,
        content={"detail": f"Unicode decoding error: {str(exc)}"}
    )

# Добавляем статические файлы
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Создаем папку для изображений в статической директории
os.makedirs("app/static/images", exist_ok=True)

# Монтируем платную галерею как статику
try:
    repo_root = Path(__file__).resolve().parents[1]
    paid_gallery_dir = repo_root / "paid_gallery"
    if paid_gallery_dir.exists():
        app.mount("/paid_gallery", StaticFiles(directory=str(paid_gallery_dir), html=True), name="paid_gallery")
        logger.info(f"[OK] Смонтирована платная галерея: {paid_gallery_dir}")
    else:
        logger.warning(f"Папка платной галереи не найдена: {paid_gallery_dir}")
except Exception as e:
    logger.error(f"Ошибка монтирования платной галереи: {e}")

# Подключаем роутеры аутентификации
try:
    from app.auth.routers import auth_router
    from app.auth.oauth_routers import oauth_router
    app.include_router(auth_router)
    app.include_router(oauth_router)
    logger.info("[OK] Роутеры аутентификации подключены")
except Exception as e:
    logger.error(f"[ERROR] Ошибка подключения роутеров аутентификации: {e}")
    import traceback
    logger.error(f"Traceback: {traceback.format_exc()}")

# Роутер generation удален - используется только /api/v1/generate-image/ в main.py

try:
    logger.info("🔄 Импортируем chat_router...")
    from app.chat_bot.api.chat_endpoints import router as chat_router
    logger.info("[OK] chat_router импортирован успешно")
    
    logger.info("🔄 Импортируем character_router...")
    from app.chat_bot.api.character_endpoints import router as character_router
    logger.info("[OK] character_router импортирован успешно")
    
    logger.info("🔄 Подключаем chat_router...")
    app.include_router(chat_router)
    logger.info("[OK] chat_router подключен")
    
    logger.info("🔄 Подключаем character_router...")
    app.include_router(character_router)
    logger.info("[OK] character_router подключен")
    
    # Подключаем новые роутеры для системы персонажей
    logger.info("🔄 Импортируем новые роутеры персонажей...")
    from app.chat_bot.add_character import character_router as new_character_router
    from app.chat_bot.add_character import universal_chat_router
    logger.info("[OK] Новые роутеры импортированы")
    
    logger.info("🔄 Подключаем new_character_router...")
    app.include_router(new_character_router)
    logger.info("[OK] new_character_router подключен")
    
    logger.info("🔄 Подключаем universal_chat_router...")
    app.include_router(universal_chat_router)
    logger.info("[OK] universal_chat_router подключен")
    
    logger.info("[OK] Роутеры chat и character подключены")

except Exception as e:
    logger.error(f"[ERROR] Ошибка подключения роутеров chat/character: {e}")
    logger.error(f"Тип ошибки: {type(e).__name__}")
    import traceback
    logger.error(f"Traceback: {traceback.format_exc()}")

# Подключаем роутер подписок (исправленная версия)
try:
    logger.info("🔄 Импортируем profit_activate_router...")
    from app.api.endpoints.profit_activate_endpoints import router as profit_activate_router
    logger.info("[OK] profit_activate_router импортирован успешно")
    
    logger.info("🔄 Подключаем profit_activate_router...")
    app.include_router(profit_activate_router, prefix="/api/v1/profit", tags=["profit"])
    logger.info("[OK] profit_activate_router подключен")
    
    logger.info("[OK] Роутер подписок (исправленный) подключен")
except Exception as e:
    logger.error(f"[ERROR] Ошибка подключения роутера подписок: {e}")
    import traceback
    logger.error(f"Traceback: {traceback.format_exc()}")

# Подключаем старый роутер подписок для обратной совместимости
try:
    logger.info("🔄 Импортируем subscription_router...")
    from app.api.endpoints.subscription_endpoints import router as subscription_router
    logger.info("[OK] subscription_router импортирован успешно")
    
    logger.info("🔄 Подключаем subscription_router...")
    app.include_router(subscription_router, prefix="/api/v1/subscription", tags=["subscription"])
    logger.info("[OK] subscription_router подключен")
    
    logger.info("[OK] Роутер подписок (старый) подключен")
except Exception as e:
    logger.error(f"[ERROR] Ошибка подключения старого роутера подписок: {e}")
    import traceback
    logger.error(f"Traceback: {traceback.format_exc()}")

# Добавляем эндпоинты напрямую в main.py для немедленного использования
from fastapi import Depends, HTTPException, status
from app.auth.dependencies import get_current_user
from app.models.user import Users
from app.services.profit_activate import ProfitActivateService
from app.schemas.subscription import SubscriptionActivateRequest, SubscriptionActivateResponse, SubscriptionStatsResponse
from app.database.db_depends import get_db
from sqlalchemy.ext.asyncio import AsyncSession

@app.post("/api/v1/profit/activate/", response_model=SubscriptionActivateResponse)
async def activate_subscription_direct(
    request: SubscriptionActivateRequest,
    current_user: Users = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Активирует подписку для пользователя (прямой эндпоинт)."""
    try:
        service = ProfitActivateService(db)
        
        if request.subscription_type.lower() not in ["base", "standard"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Поддерживаются только подписки типа 'base' и 'standard'"
            )
        
        subscription = await service.activate_subscription(current_user.id, request.subscription_type)
        
        if request.subscription_type.lower() == "base":
            message = "Подписка Base успешно активирована! Вы получили 100 кредитов и 10 генераций фото."
        else:
            message = "Подписка Standard успешно активирована! Вы получили 2000 кредитов"
        
        return SubscriptionActivateResponse(
            success=True,
            message=message,
            subscription=SubscriptionStatsResponse(
                subscription_type=subscription.subscription_type.value,
                status=subscription.status.value,
                monthly_credits=subscription.monthly_credits,
                monthly_photos=subscription.monthly_photos,
                used_credits=subscription.used_credits,
                used_photos=subscription.used_photos,
                credits_remaining=subscription.credits_remaining,
                photos_remaining=subscription.photos_remaining,
                days_left=subscription.days_until_expiry,
                is_active=subscription.is_active,
                expires_at=subscription.expires_at,
                last_reset_at=subscription.last_reset_at
            )
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка активации подписки: {str(e)}"
        )

@app.get("/api/v1/profit/stats/")
async def get_subscription_stats_direct(
    current_user: Users = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Получает статистику подписки пользователя (прямой эндпоинт)."""
    try:
        service = ProfitActivateService(db)
        stats = await service.get_subscription_stats(current_user.id)
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка получения статистики подписки: {str(e)}"
        )

# Подключаем роутер платной галереи (отдельно от других роутеров)
try:
    from app.routers.gallery import router as gallery_router
    app.include_router(gallery_router)
    logger.info("[OK] Роутер paid-gallery подключен")
except Exception as e:
    logger.error(f"[ERROR] Ошибка подключения роутера gallery: {e}")
    import traceback
    logger.error(f"Traceback: {traceback.format_exc()}")

# Подключаем роутер фотографий персонажей
try:
    from app.api.endpoints.photos_endpoints import router as photos_router
    app.include_router(photos_router)
    logger.info("[OK] Роутер фотографий персонажей подключен")
except Exception as e:
    logger.error(f"[ERROR] Ошибка подключения роутера фотографий: {e}")
    import traceback
    logger.error(f"Traceback: {traceback.format_exc()}")

# Подключаем роутер истории чата
try:
    logger.info("🔄 Подключаем роутер истории чата...")
    from app.api.endpoints.chat_history import router as chat_history_router
    app.include_router(chat_history_router, prefix="/api/v1/chat-history", tags=["chat-history"])
    logger.info("[OK] chat_history_router подключен")
    
    logger.info("[OK] Роутер истории чата подключен")
except Exception as e:
    logger.error(f"[ERROR] Ошибка подключения роутера истории чата: {e}")
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
    """Главная страница с чатом."""
    return FileResponse("app/static/chat.html")

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
        # Получаем информацию о модели
        try:
            import sys
            from pathlib import Path
            webui_path = Path(__file__).parent.parent / "stable-diffusion-webui"
            sys.path.insert(0, str(webui_path))
            from model_config import get_model_info, check_model_files
            model_info = get_model_info()
            model_available = check_model_files()
        except Exception as e:
            logger.warning(f"Не удалось получить информацию о модели: {e}")
            model_info = None
            model_available = False
        
        # Общий статус приложения
        app_status = {
            "app": "Stable Diffusion API",
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
            "model": {
                "name": model_info["name"] if model_info else "Unknown",
                "size_mb": model_info["size_mb"] if model_info else 0,
                "available": model_available,
                "vae": model_info["vae_name"] if model_info and model_info["vae_name"] else "Built-in"
            },
            "services": {}
        }
        
        # Логируем информацию о модели
        if model_info:
            logger.info(f"[TARGET] Активная модель: {model_info['name']} ({model_info['size_mb']} MB)")
            if model_info["vae_name"]:
                logger.info(f"[ART] VAE: {model_info['vae_name']}")
            else:
                logger.info("[ART] VAE: Встроенный")
        else:
            logger.warning("[WARNING] Информация о модели недоступна")
        
        return app_status
        
    except Exception as e:
        logger.error(f"Ошибка проверки здоровья приложения: {e}")
        return {
            "app": "Stable Diffusion API",
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.get("/api/v1/models/")
async def get_available_models():
    """Получить список доступных моделей."""
    return [
        {
            "id": "L3-DARKEST-PLANET-16.5B",
            "name": "L3-DARKEST-PLANET-16.5B",
            "description": "L3-DARKEST-PLANET оптимизирован для 4096 контекст - лучшая производительность для 16.5B модели"
        },
        {
            "id": "MythoMax-L2-13B",
            "name": "MythoMax L2 13B", 
            "description": "Модель для творческих задач и диалогов"
        }
    ]

@app.get("/api/v1/generation-settings/")
async def get_generation_settings():
    """Получить настройки генерации по умолчанию."""
    try:
        from app.config.generation_defaults import get_generation_params, get_fallback_values
        settings = get_generation_params("default")
        fallback_values = get_fallback_values()
        
        # Возвращаем только основные настройки для фронтенда
        return {
            "steps": settings.get("steps", fallback_values["steps"]),
            "width": settings.get("width", fallback_values["width"]),
            "height": settings.get("height", fallback_values["height"]),
            "cfg_scale": settings.get("cfg_scale", fallback_values["cfg_scale"]),
            "sampler_name": settings.get("sampler_name", fallback_values["sampler_name"]),
            "negative_prompt": fallback_values["negative_prompt"]
        }
    except Exception as e:
        logger.error(f"Ошибка получения настроек генерации: {e}")
        # Возвращаем значения по умолчанию в случае ошибки
        try:
            from app.config.generation_defaults import get_fallback_values
            return get_fallback_values()
        except Exception as fallback_error:
            logger.error(f"Ошибка получения fallback значений: {fallback_error}")
            # Последний резерв - используем default_prompts.py
            try:
                from app.config.default_prompts import get_default_negative_prompts
                from app.config.generation_defaults import DEFAULT_GENERATION_PARAMS
                return {
                    "steps": DEFAULT_GENERATION_PARAMS.get("steps", 100),
                    "width": DEFAULT_GENERATION_PARAMS.get("width", 512),
                    "height": DEFAULT_GENERATION_PARAMS.get("height", 853),
                    "cfg_scale": DEFAULT_GENERATION_PARAMS.get("cfg_scale", 5),
                    "sampler_name": DEFAULT_GENERATION_PARAMS.get("sampler_name", "Euler"),
                    "negative_prompt": get_default_negative_prompts()
                }
            except Exception as final_error:
                logger.error(f"Критическая ошибка загрузки промптов: {final_error}")
                # Последний резерв - минимальные значения
                return {
                    "steps": None,
                    "width": None,
                    "height": None,
                    "cfg_scale": None,
                    "sampler_name": None,
                    "negative_prompt": None
                }

@app.get("/api/v1/fallback-settings/")
async def get_fallback_settings():
    """Получить fallback настройки из generation_defaults.py."""
    try:
        from app.config.generation_defaults import get_fallback_values
        return get_fallback_values()
    except Exception as e:
        logger.error(f"Ошибка получения fallback настроек: {e}")
        # Последний резерв - используем default_prompts.py
        try:
            from app.config.default_prompts import get_default_negative_prompts
            from app.config.generation_defaults import DEFAULT_GENERATION_PARAMS
            return {
                "steps": DEFAULT_GENERATION_PARAMS.get("steps", 100),
                "width": DEFAULT_GENERATION_PARAMS.get("width", 512),
                "height": DEFAULT_GENERATION_PARAMS.get("height", 853),
                "cfg_scale": DEFAULT_GENERATION_PARAMS.get("cfg_scale", 5),
                "sampler_name": DEFAULT_GENERATION_PARAMS.get("sampler_name", "Euler"),
                "negative_prompt": get_default_negative_prompts()
            }
        except Exception as final_error:
            logger.error(f"Критическая ошибка загрузки промптов: {final_error}")
            # Последний резерв - минимальные значения
            return {
                "steps": None,
                "width": None,
                "height": None,
                "cfg_scale": None,
                "sampler_name": None,
                "negative_prompt": None
            }

@app.get("/api/v1/prompts/")
async def get_prompts():
    """Получить промпты из default_prompts.py."""
    try:
        from app.config.generation_defaults import get_prompts_from_defaults
        return get_prompts_from_defaults()
    except Exception as e:
        logger.error(f"Ошибка получения промптов: {e}")
        # Последний резерв - минимальные значения
        return {
            "positive_prompt": None,
            "negative_prompt": None
        }

@app.get("/api/v1/characters/{character_name}")
async def get_character_by_name(character_name: str, current_user: Users = Depends(get_current_user)):
    """Получить персонажа по имени с проверкой прав."""
    try:
        from app.chat_bot.utils.character_importer import character_importer
        from app.database.db import async_session_maker
        from app.chat_bot.models.models import CharacterDB
        from sqlalchemy import select
        
        async with async_session_maker() as db:
            result = await db.execute(
                select(CharacterDB).filter(CharacterDB.name == character_name)
            )
            character = result.scalar_one_or_none()
            
            if not character:
                raise HTTPException(status_code=404, detail="Персонаж не найден")
            
            # Проверяем права на редактирование
            if character.user_id != current_user.id and not current_user.is_admin:
                raise HTTPException(status_code=403, detail="Нет прав на редактирование этого персонажа")
            
            return {
                "id": character.id,
                "name": character.name,
                "display_name": character.display_name,
                "description": character.description,
                "prompt": character.prompt,
                "character_appearance": character.character_appearance,
                "location": character.location,
                "user_id": character.user_id
            }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка получения персонажа {character_name}: {e}")
        raise HTTPException(status_code=500, detail="Ошибка получения персонажа")

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
                    "display_name": char.display_name,
                    "description": char.description,
                    "prompt": char.prompt,
                    "character_appearance": char.character_appearance,
                    "location": char.location,
                    "user_id": char.user_id
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
                    "display_name": char.display_name,
                    "description": char.description,
                    "prompt": char.prompt,
                    "character_appearance": char.character_appearance,
                    "location": char.location,
                    "user_id": char.user_id
                })
            
            logger.info(f"Загружено персонажей: {len(character_list)}")
            return character_list
    except Exception as e:
        logger.error(f"Ошибка загрузки персонажей: {e}")
        return []

@app.post("/api/chat/")
async def legacy_chat_redirect(request: Request):
    return RedirectResponse(url="/api/v1/chat/")



@app.post("/chat")
async def chat_endpoint(request: dict):
    """
    Простой эндпоинт для чата - прямой ответ от модели без пост-обработки.
    """
    try:
        logger.info("[NOTE] /chat: Простой режим - прямой ответ от модели")
        
        # Импортируем необходимые модули
        from app.chat_bot.services.textgen_webui_service import textgen_webui_service
        from app.chat_bot.config.chat_config import chat_config
        from app.config.generation_defaults import get_generation_params
        from app.services.profit_activate import ProfitActivateService
        from app.database.db import async_session_maker
        import json
        
        # Проверяем подключение к text-generation-webui
        if not await textgen_webui_service.check_connection():
            raise HTTPException(
                status_code=503, 
                detail="text-generation-webui недоступен. Запустите сервер text-generation-webui."
            )
        
        # Простая валидация запроса
        message = request.get("message", "").strip()
        character_name = request.get("character", "anna")  # По умолчанию Anna
        if not message:
            raise HTTPException(status_code=400, detail="Сообщение не может быть пустым")
        
        history = request.get("history", [])
        session_id = request.get("session_id", "default")
        
        # Проверяем монеты пользователя (если авторизован)
        user_id = request.get("user_id")  # Будет передаваться с фронтенда
        if user_id:
            logger.info(f"[DEBUG] DEBUG: Проверка монет для сообщения пользователя {user_id}")
            async with async_session_maker() as db:
                from app.services.coins_service import CoinsService
                coins_service = CoinsService(db)
                can_send_message = await coins_service.can_user_send_message(user_id)
                logger.info(f"[DEBUG] DEBUG: Может отправить сообщение: {can_send_message}")
                if not can_send_message:
                    coins = await coins_service.get_user_coins(user_id)
                    logger.error(f"[ERROR] DEBUG: Недостаточно монет! У пользователя {user_id}: {coins} монет, нужно 2")
                    raise HTTPException(
                        status_code=403, 
                        detail="Недостаточно монет для отправки сообщения! Нужно 2 монеты."
                    )
                else:
                    logger.info(f"[OK] DEBUG: Пользователь {user_id} может отправить сообщение")
        
        # Получаем данные персонажа из базы данных
        from app.database.db import async_session_maker
        from app.chat_bot.models.models import CharacterDB
        from sqlalchemy import select
        
        character_data = None
        try:
            async with async_session_maker() as db:
                # Поиск без учета регистра
                result = await db.execute(
                    select(CharacterDB).where(CharacterDB.name.ilike(character_name))
                )
                db_character = result.scalar_one_or_none()
                
                if db_character:
                    character_data = {
                        "name": db_character.name,
                        "prompt": db_character.prompt
                    }
                    logger.info(f"[OK] Данные персонажа '{character_name}' получены из БД")
                else:
                    # Fallback к файлам
                    character_data = get_character_data(character_name)
                    if character_data:
                        logger.info(f"[OK] Fallback: данные персонажа '{character_name}' получены из файлов")
                    else:
                        logger.error(f"[ERROR] Персонаж '{character_name}' не найден ни в БД, ни в файлах")
                        raise HTTPException(
                            status_code=404, 
                            detail=f"Персонаж '{character_name}' не найден"
                        )
        except Exception as e:
            logger.error(f"[ERROR] Ошибка получения данных персонажа: {e}")
            # Fallback к файлам
            character_data = get_character_data(character_name)
            if not character_data:
                raise HTTPException(
                    status_code=404, 
                    detail=f"Персонаж '{character_name}' не найден"
                )
        
        # Специальная обработка для "continue the story"
        is_continue_story = message.lower().strip() == "continue the story briefly"
        
        if is_continue_story:
            logger.info(f"📖 Continue the story briefly - продолжаем историю кратко")
        else:
            logger.info(f"[START] Генерируем ответ для: {message[:50]}...")
        
        # Строим простой промпт в формате Alpaca
        if history:
            # Строим историю в формате Alpaca
            history_text = ""
            for msg in history[-10:]:  # Последние 10 сообщений
                if msg.get('role') == 'user':
                    user_content = msg.get('content', '')
                    history_text += f"### Instruction:\n{user_content}\n\n### Response:\n"
                elif msg.get('role') == 'assistant':
                    history_text += f"{msg.get('content', '')}\n\n"
            
            # Строим промпт
            full_prompt = character_data["prompt"] + "\n\n" + history_text
        else:
            # Если истории нет
            if is_continue_story:
                full_prompt = character_data["prompt"] + f"\n\n### Instruction:\ncontinue the story briefly.\n\n### Response:\n"
            else:
                full_prompt = character_data["prompt"] + f"\n\n### Instruction:\n{message}\n\n### Response:\n"
        
        # Генерируем ответ напрямую от модели
        response = await textgen_webui_service.generate_text(
            prompt=full_prompt,
            max_tokens=chat_config.HARD_MAX_TOKENS,
            temperature=chat_config.DEFAULT_TEMPERATURE,
            top_p=chat_config.DEFAULT_TOP_P,
            top_k=chat_config.DEFAULT_TOP_K,
            min_p=chat_config.DEFAULT_MIN_P,
            repeat_penalty=chat_config.DEFAULT_REPEAT_PENALTY,
            presence_penalty=chat_config.DEFAULT_PRESENCE_PENALTY
        )
        
        if not response:
            raise HTTPException(
                status_code=500, 
                detail="Не удалось сгенерировать ответ от модели"
            )
        
        logger.info(f"[OK] /chat: Ответ сгенерирован ({len(response)} символов)")
        
        # Тратим монеты за сообщение (если пользователь авторизован)
        if user_id:
            logger.info(f"💰 Тратим 2 монеты за сообщение для пользователя {user_id}")
            async with async_session_maker() as db:
                from app.services.coins_service import CoinsService
                coins_service = CoinsService(db)
                coins_spent = await coins_service.spend_coins_for_message(user_id)
                if coins_spent:
                    coins_left = await coins_service.get_user_coins(user_id)
                    logger.info(f"[OK] Потрачено 2 монеты за сообщение для пользователя {user_id}. Осталось: {coins_left}")
                else:
                    logger.warning(f"[WARNING] Не удалось потратить монеты для пользователя {user_id}")
        
        # Проверяем, нужно ли генерировать изображение
        generate_image = request.get("generate_image", False)
        image_url = None
        image_filename = None
        
        if generate_image:
            try:
                logger.info("[ART] Генерируем изображение для чата...")
                
                # Проверяем, может ли пользователь генерировать фото
                if user_id:
                    logger.info(f"[DEBUG] DEBUG: Проверка монет для генерации фото пользователя {user_id}")
                    async with async_session_maker() as db:
                        from app.services.coins_service import CoinsService
                        coins_service = CoinsService(db)
                        can_generate_photo = await coins_service.can_user_generate_photo(user_id)
                        logger.info(f"[DEBUG] DEBUG: Может генерировать фото: {can_generate_photo}")
                        if not can_generate_photo:
                            coins = await coins_service.get_user_coins(user_id)
                            logger.error(f"[ERROR] DEBUG: Недостаточно монет для генерации фото! У пользователя {user_id}: {coins} монет, нужно 30")
                            raise HTTPException(
                                status_code=403, 
                                detail="Недостаточно монет для генерации фото! Нужно 30 монет."
                            )
                        else:
                            logger.info(f"[OK] DEBUG: Пользователь {user_id} может генерировать фото")
                else:
                    logger.warning(f"[WARNING] DEBUG: user_id не передан, пропускаем проверку монет")
                
                # Получаем промпт для изображения
                image_prompt = request.get("image_prompt") or message
                
                # Получаем параметры генерации изображения
                image_steps = request.get("image_steps")
                image_width = request.get("image_width") 
                image_height = request.get("image_height")
                image_cfg_scale = request.get("image_cfg_scale")
                
                # Создаем запрос для генерации изображения
                image_request = ImageGenerationRequest(
                    prompt=image_prompt,
                    character=character_name,
                    steps=image_steps,
                    width=image_width,
                    height=image_height,
                    cfg_scale=image_cfg_scale
                )
                
                # Вызываем существующий эндпоинт генерации изображений через HTTP
                import httpx
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        "http://localhost:8000/api/v1/generate-image/",
                        json=image_request.dict()
                    )
                    if response.status_code == 200:
                        image_result = response.json()
                        image_url = image_result.get("image_url")
                        image_filename = image_result.get("filename")
                    else:
                        raise Exception(f"Ошибка генерации изображения: {response.status_code}")
                
                logger.info(f"[OK] /chat: Изображение сгенерировано: {image_filename}")
                
                # Проверяем доступность изображения
                if image_url:
                    import os
                    static_path = f"app/static/images/{image_filename}"
                    if os.path.exists(static_path):
                        logger.info(f"[OK] DEBUG: Файл изображения существует: {static_path}")
                    else:
                        logger.error(f"[ERROR] DEBUG: Файл изображения не найден: {static_path}")
                        image_url = None
                
                # Тратим монеты за генерацию фото (если пользователь авторизован)
                if user_id and image_url:
                    logger.info(f"💰 Тратим 30 монет за генерацию фото для пользователя {user_id}")
                    async with async_session_maker() as db:
                        from app.services.coins_service import CoinsService
                        coins_service = CoinsService(db)
                        coins_spent = await coins_service.spend_coins_for_photo(user_id)
                        if coins_spent:
                            coins_left = await coins_service.get_user_coins(user_id)
                            logger.info(f"[OK] Потрачено 30 монет за генерацию фото для пользователя {user_id}. Осталось: {coins_left}")
                        else:
                            logger.warning(f"[WARNING] Не удалось потратить монеты за генерацию фото для пользователя {user_id}")
                
            except Exception as e:
                logger.error(f"[ERROR] /chat: Ошибка генерации изображения: {e}")
                # Продолжаем без изображения, не прерываем чат
        
        # Возвращаем ответ с изображением (если есть)
        result = {
            "response": response,
            "session_id": session_id,
            "character": character_data["name"],
            "message": message,
            "image_generated": generate_image and image_url is not None
        }
        
        logger.info(f"[DEBUG] DEBUG: image_url = {image_url}, image_filename = {image_filename}")
        logger.info(f"[DEBUG] DEBUG: generate_image = {generate_image}, image_generated = {result['image_generated']}")
        
        if image_url:
            result["image_url"] = image_url
            result["image_filename"] = image_filename
            logger.info(f"[OK] DEBUG: Добавлено изображение в ответ: {image_url}")
        else:
            logger.warning(f"[WARNING] DEBUG: image_url пустой, изображение не добавлено в ответ")
        
        return result
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[ERROR] /chat: Ошибка: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Импорт уже есть выше в файле

@app.post("/api/v1/generate-image/")
async def generate_image(request: ImageGenerationRequest):
    """
    Генерация изображения для чата.

    Args:
        request (ImageGenerationRequest): Запрос с параметрами генерации.

    Returns:
        dict: Результат генерации изображения.
    """
    try:
        # Проверяем подписку пользователя (если авторизован)
        user_id = getattr(request, 'user_id', None)
        logger.info(f"[DEBUG] DEBUG: Эндпоинт generate-image, user_id: {user_id}")
        if user_id:
            logger.info(f"[DEBUG] DEBUG: Проверка монет для генерации фото пользователя {user_id}")
            from app.services.coins_service import CoinsService
            from app.database.db import async_session_maker
            
            async with async_session_maker() as db:
                coins_service = CoinsService(db)
                can_generate_photo = await coins_service.can_user_generate_photo(user_id)
                logger.info(f"[DEBUG] DEBUG: Может генерировать фото: {can_generate_photo}")
                if not can_generate_photo:
                    coins = await coins_service.get_user_coins(user_id)
                    logger.error(f"[ERROR] DEBUG: Недостаточно монет для генерации фото! У пользователя {user_id}: {coins} монет, нужно 30")
                    raise HTTPException(
                        status_code=403, 
                        detail="Недостаточно монет для генерации фото! Нужно 30 монет."
                    )
                else:
                    logger.info(f"[OK] DEBUG: Пользователь {user_id} может генерировать фото")
        else:
            logger.warning(f"[WARNING] DEBUG: user_id не передан в эндпоинте generate-image")
        # Логируем информацию о модели перед генерацией
        try:
            import sys
            from pathlib import Path
            webui_path = Path(__file__).parent.parent / "stable-diffusion-webui"
            sys.path.insert(0, str(webui_path))
            from model_config import get_model_info
            model_info = get_model_info()
            if model_info:
                logger.info(f"[TARGET] Генерация изображения с моделью: {model_info['name']} ({model_info['size_mb']} MB)")
            else:
                logger.warning("[WARNING] Информация о модели недоступна")
        except Exception as e:
            logger.warning(f"[WARNING] Не удалось получить информацию о модели: {e}")
        
        logger.info(f"[TARGET] Генерация изображения: {request.prompt}")

        # Создаем сервис для генерации
        face_refinement_service = FaceRefinementService(settings.SD_API_URL)

        # Получаем данные персонажа для внешности
        character_name = request.character or "anna"
        
        # Сначала пытаемся получить данные из базы данных
        character_appearance = None
        character_location = None
        
        try:
            from app.database.db import async_session_maker
            from app.chat_bot.models.models import CharacterDB
            from sqlalchemy import select
            
            async with async_session_maker() as db:
                # Поиск без учета регистра
                result = await db.execute(
                    select(CharacterDB).where(CharacterDB.name.ilike(character_name))
                )
                db_character = result.scalar_one_or_none()
                
                if db_character:
                    character_appearance = db_character.character_appearance
                    character_location = db_character.location
                    logger.info(f"[OK] Данные персонажа '{character_name}' получены из БД")
                else:
                    # Если в БД нет, пытаемся получить из файлов
                    character_data = get_character_data(character_name)
                    if character_data:
                        character_appearance = character_data.get("character_appearance")
                        character_location = character_data.get("location")
                        logger.info(f"[OK] Данные персонажа '{character_name}' получены из файлов")
                    else:
                        logger.error(f"[ERROR] Персонаж '{character_name}' не найден ни в БД, ни в файлах")
                        raise HTTPException(status_code=404, detail=f"Персонаж '{character_name}' не найден")
                        
        except Exception as e:
            logger.error(f"[ERROR] Ошибка получения данных персонажа: {e}")
            # Fallback к файлам
            character_data = get_character_data(character_name)
            if character_data:
                character_appearance = character_data.get("character_appearance")
                character_location = character_data.get("location")
                logger.info(f"[OK] Fallback: данные персонажа '{character_name}' получены из файлов")
            else:
                logger.error(f"[ERROR] Персонаж '{character_name}' не найден")
                raise HTTPException(status_code=404, detail=f"Персонаж '{character_name}' не найден")
        # Импортируем настройки по умолчанию
        from app.config.generation_defaults import get_generation_params
        
        # Получаем настройки по умолчанию
        default_params = get_generation_params("default")
        logger.info(f"🚨 ДИАГНОСТИКА: default_params['steps'] = {default_params.get('steps')}")
        
        # Создаем настройки генерации с использованием значений по умолчанию
        generation_settings = GenerationSettings(
            prompt=request.prompt,
            negative_prompt=request.negative_prompt,
            use_default_prompts=request.use_default_prompts,
            character=character_name,
            seed=request.seed or default_params.get("seed", -1),
            steps=default_params.get("steps"),  # ИСПРАВЛЕНО: всегда используем значение из конфигурации
            width=request.width or default_params.get("width"),
            height=request.height or default_params.get("height"),
            cfg_scale=request.cfg_scale or default_params.get("cfg_scale"),
            sampler_name=request.sampler_name or default_params.get("sampler_name"),
            batch_size=default_params.get("batch_size", 1),
            n_iter=default_params.get("n_iter", 1),
            save_grid=default_params.get("save_grid", False),
            use_adetailer=default_params.get("use_adetailer", False),
            enable_hr=default_params.get("enable_hr", True),
            denoising_strength=default_params.get("denoising_strength", 0.5),
            hr_scale=default_params.get("hr_scale", 1.5),
            hr_upscaler=default_params.get("hr_upscaler", "R-ESRGAN 4x+ Anime6B"),
            hr_second_pass_steps=default_params.get("hr_second_pass_steps", 10),
            hr_prompt=default_params.get("hr_prompt", ""),
            hr_negative_prompt=default_params.get("hr_negative_prompt", ""),
            restore_faces=default_params.get("restore_faces", False),
            clip_skip=default_params.get("clip_skip", 2),
            lora_models=default_params.get("lora_models", []),
            alwayson_scripts=default_params.get("alwayson_scripts", {})
        )
        
        # Создаем полные настройки для логирования (включая все значения по умолчанию)
        full_settings_for_logging = default_params.copy()
        full_settings_for_logging.update({
            "prompt": request.prompt,
            "negative_prompt": request.negative_prompt,
            "use_default_prompts": request.use_default_prompts,
            "character": character_name,
            "seed": request.seed or default_params.get("seed", -1),
            "steps": request.steps or default_params.get("steps", 35),
            "width": request.width or default_params.get("width", 512),
            "height": request.height or default_params.get("height", 853),
            "cfg_scale": request.cfg_scale or default_params.get("cfg_scale", 12),
            "sampler_name": request.sampler_name or default_params.get("sampler_name", "DPM++ 2M Karras"),
        })
        
        # Добавляем внешность и локацию персонажа в промпт если есть
        prompt_parts = []
        
        if character_appearance:
            logger.info(f"[ART] Добавляем внешность персонажа: {character_appearance[:100]}...")
            prompt_parts.append(character_appearance)
            full_settings_for_logging["character_appearance"] = character_appearance
        
        if character_location:
            logger.info(f"🏠 Добавляем локацию персонажа: {character_location[:100]}...")
            prompt_parts.append(character_location)
            full_settings_for_logging["character_location"] = character_location
        
        # Получаем стандартный промпт из default_prompts.py
        from app.config.default_prompts import get_default_positive_prompts
        default_positive_prompts = get_default_positive_prompts()
        logger.info(f"[NOTE] Добавляем стандартный промпт: {default_positive_prompts[:100]}...")
        
        # Формируем финальный промпт: данные персонажа + пользовательский промпт + стандартный промпт
        final_prompt_parts = []
        
        # 1. Данные персонажа (если есть)
        if prompt_parts:
            final_prompt_parts.extend(prompt_parts)
        
        # 2. Пользовательский промпт
        final_prompt_parts.append(generation_settings.prompt)
        
        # 3. Стандартный промпт
        final_prompt_parts.append(default_positive_prompts)
        
        # Объединяем все части
        enhanced_prompt = ", ".join(final_prompt_parts)
        generation_settings.prompt = enhanced_prompt
        
        # Обновляем промпт в настройках для логирования
        full_settings_for_logging["prompt"] = enhanced_prompt
        full_settings_for_logging["default_positive_prompts"] = default_positive_prompts
        
        # Генерируем изображение
        result = await face_refinement_service.generate_image(generation_settings, full_settings_for_logging)
        
        if not result.image_data or len(result.image_data) == 0:
            raise HTTPException(status_code=500, detail="Не удалось сгенерировать изображение")
        
        # Берем первое изображение
        image_data = result.image_data[0]
        
        # Сохраняем изображение
        from app.utils.image_saver import save_image
        import time
        
        # Создаем папку для персонажа
        character_name = request.character or "character"
        character_photos_dir = f"paid_gallery/main_photos/{character_name.lower()}"
        os.makedirs(character_photos_dir, exist_ok=True)
        
        # Сохраняем изображение
        filename = f"generated_{int(time.time())}.png"
        filepath = os.path.join(character_photos_dir, filename)
        
        with open(filepath, 'wb') as f:
            f.write(image_data)
        
        # Возвращаем URL изображения в правильном формате
        image_url = f"/static/photos/{character_name.lower()}/{filename}"
        
        # Проверяем, что файл действительно существует
        if os.path.exists(filepath):
            logger.info(f"[OK] Изображение сохранено: {filepath}")
            logger.info(f"[OK] URL изображения: {image_url}")
        else:
            logger.error(f"[ERROR] Файл не найден после сохранения: {filepath}")
            image_url = None
        
        # Тратим монеты за генерацию фото (если пользователь авторизован)
        if user_id:
            logger.info(f"💰 Тратим 30 монет за генерацию фото для пользователя {user_id}")
            async with async_session_maker() as db:
                from app.services.coins_service import CoinsService
                coins_service = CoinsService(db)
                coins_spent = await coins_service.spend_coins_for_photo(user_id)
                if coins_spent:
                    coins_left = await coins_service.get_user_coins(user_id)
                    logger.info(f"[OK] Потрачено 30 монет за генерацию фото для пользователя {user_id}. Осталось: {coins_left}")
                else:
                    logger.warning(f"[WARNING] Не удалось потратить монеты за генерацию фото для пользователя {user_id}")
        
        return {
            "image_url": image_url,
            "filename": filename,
            "message": "Изображение успешно сгенерировано"
        }
        
    except Exception as e:
        logger.error(f"[ERROR] Ошибка генерации изображения: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка генерации изображения: {str(e)}")



if __name__ == "__main__":
    logger.info("Запуск основного приложения...")
    uvicorn.run(app, host="0.0.0.0", port=8000)