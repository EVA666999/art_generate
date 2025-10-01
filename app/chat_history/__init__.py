"""
Модуль истории чата.

Этот модуль содержит всю логику для работы с историей чата:
- Модели базы данных
- Сервисы для работы с историей
- API эндпоинты
- Проверка прав доступа на основе подписки

Структура:
- models/ - модели базы данных
- services/ - бизнес-логика
- api/ - API эндпоинты
"""

from app.chat_history.api.endpoints import router as chat_history_router

__all__ = [
    "chat_history_router"
]
