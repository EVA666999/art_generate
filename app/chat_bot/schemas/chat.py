"""
Схемы данных для чат-бота с настраиваемым характером.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
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
    
    # Параметры генерации изображений
    generate_image: Optional[bool] = Field(
        default=False, 
        description="Генерировать изображение вместе с текстовым ответом"
    )
    image_prompt: Optional[str] = Field(
        default=None, 
        description="Промпт для генерации изображения (если не указан, используется message)"
    )
    image_steps: Optional[int] = Field(
        default=None, 
        description="Количество шагов для генерации изображения"
    )
    image_width: Optional[int] = Field(
        default=None, 
        description="Ширина изображения"
    )
    image_height: Optional[int] = Field(
        default=None, 
        description="Высота изображения"
    )
    image_cfg_scale: Optional[float] = Field(
        default=None, 
        description="CFG Scale для генерации изображения"
    )


class CharacterConfig(BaseModel):
    """Упрощенная конфигурация персонажа в формате Alpaca."""
    # Основные характеристики
    name: str = Field(..., description="Уникальное имя персонажа")
    
    # Единый промпт в формате Alpaca
    prompt: str = Field(
        ..., 
        description="Полный промпт персонажа в формате Alpaca"
    )
    
    # Описание внешности для генерации изображений
    character_appearance: Optional[str] = Field(
        None,
        description="Описание внешности персонажа для автоматического добавления в промпт генерации"
    )
    
    # Описание локации для генерации изображений
    location: Optional[str] = Field(
        None,
        description="Описание локации персонажа для автоматического добавления в промпт генерации"
    )
    
    # face_image удален (IP-Adapter удален)

    class Config:
        from_attributes = True


class CharacterCreate(CharacterConfig):
    """Схема для создания нового персонажа."""
    pass


class UserCharacterCreate(BaseModel):
    """Схема для создания персонажа пользователем."""
    name: str = Field(..., description="Имя персонажа")
    personality: str = Field(..., description="Имя и характер персонажа")
    situation: str = Field(..., description="Ролевая ситуация")
    instructions: str = Field(..., description="Инструкции для персонажа")
    style: Optional[str] = Field(None, description="Стиль ответа (необязательно)")
    appearance: Optional[str] = Field(None, description="Внешность персонажа для генерации фото")
    location: Optional[str] = Field(None, description="Локация персонажа для генерации фото")
    
    class Config:
        from_attributes = True
        # Настройки для правильной работы с Unicode
        json_encoders = {
            str: lambda v: v.encode('utf-8').decode('utf-8') if isinstance(v, str) else v
        }
    
    def __init__(self, **data):
        """Инициализация с правильной обработкой Unicode."""
        # Обрабатываем все строковые поля
        for field_name, field_value in data.items():
            if isinstance(field_value, str):
                # Убеждаемся, что строка правильно закодирована
                try:
                    field_value.encode('utf-8')
                except UnicodeEncodeError:
                    # Если не может быть закодирована, заменяем проблемные символы
                    data[field_name] = field_value.encode('utf-8', errors='replace').decode('utf-8')
        
        super().__init__(**data)


class CharacterUpdate(BaseModel):
    """Схема для обновления существующего персонажа."""
    name: Optional[str] = Field(None, description="Имя персонажа")
    prompt: Optional[str] = Field(None, description="Полный промпт персонажа в формате Alpaca")
    character_appearance: Optional[str] = Field(None, description="Описание внешности персонажа")
    location: Optional[str] = Field(None, description="Описание локации персонажа")
    
    class Config:
        from_attributes = True


class CharacterInDB(CharacterConfig):
    """Схема для персонажа, хранящегося в БД."""
    id: int
    user_id: Optional[int] = Field(None, description="ID пользователя, создавшего персонажа")
    created_at: Optional[datetime] = Field(None, description="Время создания персонажа")
    main_photos: Optional[str] = Field(None, description="JSON строка с ID главных фото")

    class Config:
        from_attributes = True
        json_encoders = {
            str: lambda v: v.encode('utf-8').decode('utf-8'),
            datetime: lambda v: v.isoformat() if v else None
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
    # Поля для генерации изображений
    image_url: Optional[str] = Field(
        None, 
        description="URL сгенерированного изображения"
    )
    image_filename: Optional[str] = Field(
        None, 
        description="Имя файла сгенерированного изображения"
    )
    image_generated: Optional[bool] = Field(
        False, 
        description="Было ли сгенерировано изображение"
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