"""
Схемы данных для чат-бота с настраиваемым характером.
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class MessageRole(str, Enum):
    """Роли сообщений в диалоге."""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class ChatMessage(BaseModel):
    """Структура сообщения в диалоге."""
    role: MessageRole = Field(..., description="Роль отправителя сообщения")
    content: str = Field(..., description="Содержимое сообщения")
    timestamp: Optional[str] = Field(None, description="Временная метка сообщения")


class SimpleChatRequest(BaseModel):
    """Упрощенный запрос на генерацию ответа в чате - только сообщение пользователя."""
    message: str = Field(..., description="Сообщение пользователя для бота")


class CharacterConfig(BaseModel):
    """Конфигурация характера персонажа."""
    name: str = Field(..., description="Имя персонажа")
    personality: str = Field(..., description="Описание личности персонажа")
    background: Optional[str] = Field(None, description="Предыстория персонажа")
    speaking_style: Optional[str] = Field(None, description="Стиль речи персонажа")
    interests: Optional[List[str]] = Field(None, description="Интересы персонажа")
    mood: Optional[str] = Field(None, description="Текущее настроение персонажа")
    additional_context: Optional[Dict[str, Any]] = Field(None, description="Дополнительный контекст")
    age: Optional[str] = Field(None, description="Возраст персонажа")
    profession: Optional[str] = Field(None, description="Профессия персонажа")
    behavior: Optional[str] = Field(None, description="Поведение персонажа")
    appearance: Optional[str] = Field(None, description="Внешность персонажа")
    voice: Optional[str] = Field(None, description="Голос персонажа")
    rules: Optional[str] = Field(None, description="Правила поведения персонажа")
    context: Optional[str] = Field(None, description="Контекст ситуации")

    class Config:
        from_attributes = True


class CharacterCreate(CharacterConfig):
    """Схема для создания нового персонажа."""
    pass


class CharacterUpdate(CharacterConfig):
    """Схема для обновления существующего персонажа."""
    pass


class CharacterInDB(CharacterConfig):
    """Схема для персонажа, хранящегося в БД."""
    id: int

    class Config:
        from_attributes = True
        json_encoders = {
            str: lambda v: v.encode('utf-8').decode('utf-8')
        }


class ChatRequest(BaseModel):
    """Запрос на генерацию ответа в чате."""
    messages: List[ChatMessage] = Field(..., description="История диалога")
    max_tokens: Optional[int] = Field(default=512, description="Максимальное количество токенов в ответе")
    temperature: Optional[float] = Field(default=0.7, description="Температура генерации (0.0-1.0)")
    top_p: Optional[float] = Field(default=0.9, description="Top-p параметр для ядерной выборки")
    top_k: Optional[int] = Field(default=40, description="Top-k параметр для выборки")
    repeat_penalty: Optional[float] = Field(default=1.1, description="Штраф за повторения")
    stream: Optional[bool] = Field(False, description="Потоковая генерация ответа")


class ChatResponse(BaseModel):
    """Ответ от модели чата."""
    message: str = Field(..., description="Сгенерированный ответ")
    character_name: str = Field(..., description="Имя персонажа")
    tokens_used: Optional[int] = Field(None, description="Количество использованных токенов")
    generation_time: Optional[float] = Field(None, description="Время генерации в секундах")
    model_data: Optional[Dict[str, Any]] = Field(None, description="Информация о модели")


class ChatError(BaseModel):
    """Структура ошибки чата."""
    error: str = Field(..., description="Описание ошибки")
    error_type: str = Field(..., description="Тип ошибки")
    details: Optional[Dict[str, Any]] = Field(None, description="Детали ошибки") 