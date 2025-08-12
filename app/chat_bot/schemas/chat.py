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
    role: MessageRole = Field(
        ..., 
        description="Роль отправителя сообщения"
    )
    content: str = Field(
        ..., 
        description="Содержимое сообщения"
    )
    timestamp: Optional[str] = Field(
        None, 
        description="Временная метка сообщения"
    )


class SimpleChatRequest(BaseModel):
    """Упрощенный запрос на генерацию ответа в чате."""
    message: str = Field(
        ..., 
        description="Сообщение пользователя для бота"
    )
    history: Optional[List[Dict[str, str]]] = Field(
        default=None, 
        description="История диалога"
    )
    session_id: Optional[str] = Field(
        default=None, 
        description="Анонимный идентификатор сессии"
    )
    user: Optional[str] = Field(
        default=None, 
        description="Отображаемое имя пользователя"
    )
    
    # Параметры генерации для контроля качества ответов
    max_tokens: Optional[int] = Field(
        default=None, 
        description="Максимальное количество токенов"
    )
    temperature: Optional[float] = Field(
        default=None, 
        description="Температура генерации (0.0-1.0)"
    )
    top_p: Optional[float] = Field(
        default=None, 
        description="Top-p параметр для ядерной выборки"
    )
    top_k: Optional[int] = Field(
        default=None, 
        description="Top-k параметр для выборки"
    )
    repeat_penalty: Optional[float] = Field(
        default=None, 
        description="Штраф за повторения"
    )


class CharacterConfig(BaseModel):
    """Упрощенная конфигурация персонажа в формате Alpaca."""
    # Основные характеристики
    name: str = Field(..., description="Уникальное имя персонажа")
    
    # Alpaca формат - 3 основных поля
    instructions: str = Field(
        ..., 
        description="Instructions - правила поведения"
    )
    system_prompt: Optional[str] = Field(
        None, 
        description="System prompt - контекст истории"
    )
    response_format: Optional[str] = Field(
        None, 
        description="Response - правила ответов"
    )

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
    messages: List[ChatMessage] = Field(
        ..., 
        description="История диалога"
    )
    max_tokens: Optional[int] = Field(
        default=None, 
        description="Максимальное количество токенов"
    )
    temperature: Optional[float] = Field(
        default=0.7, 
        description="Температура генерации (0.0-1.0)"
    )
    top_p: Optional[float] = Field(
        default=0.9, 
        description="Top-p параметр для ядерной выборки"
    )
    top_k: Optional[int] = Field(
        default=40, 
        description="Top-k параметр для выборки"
    )
    repeat_penalty: Optional[float] = Field(
        default=1.1, 
        description="Штраф за повторения"
    )
    stream: Optional[bool] = Field(
        False, 
        description="Потоковая генерация ответа"
    )


class ChatResponse(BaseModel):
    """Ответ от модели чата."""
    message: str = Field(..., description="Сгенерированный ответ")
    character_name: str = Field(..., description="Имя персонажа")
    tokens_used: Optional[int] = Field(
        None, 
        description="Количество использованных токенов"
    )
    generation_time: Optional[float] = Field(
        None, 
        description="Время генерации в секундах"
    )
    model_data: Optional[Dict[str, Any]] = Field(
        None, 
        description="Информация о модели"
    )
    
    class Config:
        protected_namespaces = ()


class ChatError(BaseModel):
    """Структура ошибки чата."""
    error: str = Field(..., description="Описание ошибки")
    error_type: str = Field(..., description="Тип ошибки")
    details: Optional[Dict[str, Any]] = Field(
        None, 
        description="Детали ошибки"
    ) 