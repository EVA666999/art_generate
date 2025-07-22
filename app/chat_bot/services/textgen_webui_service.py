"""
Сервис для работы с text-generation-webui через OpenAI-совместимый API.
"""
import aiohttp
import json
from typing import List, Dict, Any, Optional, AsyncGenerator
from app.chat_bot.schemas.chat import ChatMessage, CharacterConfig, MessageRole
from app.chat_bot.config.chat_config import chat_config
from app.utils.logger import logger
from app.config.settings import settings


class TextGenWebUIService:
    """Сервис для работы с text-generation-webui через OpenAI API."""
    
    def __init__(self, server_url: Optional[str] = None):
        # Используем OpenAI API на порту 5000 из настроек
        default_url = f"http://{settings.text_generation_webui_host}:5000"
        self.server_url = (server_url or default_url).rstrip('/')
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """Асинхронный контекстный менеджер для инициализации сессии."""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=60)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Закрытие сессии при выходе из контекста."""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def check_connection(self) -> bool:
        """Проверяет подключение к text-generation-webui OpenAI API."""
        if not self.session:
            return False
        
        try:
            async with self.session.get(f"{self.server_url}/v1/models") as response:
                return response.status == 200
        except Exception as e:
            logger.error(f"Ошибка подключения к OpenAI API: {e}")
            return False
    
    async def get_models(self) -> List[Dict[str, Any]]:
        """Получает список доступных моделей через OpenAI API."""
        if not self.session:
            raise RuntimeError("Сервис не инициализирован")
        
        try:
            async with self.session.get(f"{self.server_url}/v1/models") as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("data", [])
                else:
                    raise Exception(f"Ошибка получения моделей: {response.status}")
        except Exception as e:
            logger.error(f"Ошибка получения списка моделей: {e}")
            raise
    
    async def load_model(self, model_name: str) -> bool:
        """Загружает модель в text-generation-webui (через OpenAI API)."""
        if not self.session:
            raise RuntimeError("Сервис не инициализирован")
        
        try:
            # В OpenAI API модель указывается в каждом запросе
            # Проверяем, что модель доступна
            models = await self.get_models()
            available_models = [m.get("id") for m in models]
            
            if model_name in available_models:
                logger.info(f"Модель {model_name} доступна")
                return True
            else:
                logger.warning(f"Модель {model_name} не найдена в списке доступных")
                return False
        except Exception as e:
            logger.error(f"Ошибка проверки модели {model_name}: {e}")
            return False
    
    async def generate_response(
        self,
        messages: List[ChatMessage],
        character_config: CharacterConfig,
        temperature: float = 0.7,
        max_tokens: int = 200,
        **kwargs
    ) -> tuple[str, Dict[str, Any]]:
        """Генерирует ответ через OpenAI API."""
        
        if not self.session:
            raise RuntimeError("Сервис не инициализирован")
        
        # Формируем сообщения в формате OpenAI
        openai_messages = []
        
        # Добавляем system message с конфигурацией персонажа
        system_prompt = self._format_system_prompt(character_config)
        openai_messages.append({
            "role": "system",
            "content": system_prompt
        })
        
        # Добавляем сообщения пользователя и ассистента
        for msg in messages:
            if msg.role == MessageRole.USER:
                openai_messages.append({
                    "role": "user",
                    "content": msg.content
                })
            elif msg.role == MessageRole.ASSISTANT:
                openai_messages.append({
                    "role": "assistant", 
                    "content": msg.content
                })
        
        # Параметры для OpenAI API
        payload = {
            "model": settings.text_generation_webui_model.replace('.gguf',''),
            "messages": openai_messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": kwargs.get("top_p", 0.9),
            "top_k": kwargs.get("top_k", 40),
            "repetition_penalty": kwargs.get("repeat_penalty", 1.1),
            "stop": kwargs.get("stop", ["\n\n", "Human:", "Assistant:"]),
            "stream": False
        }
        
        try:
            async with self.session.post(
                f"{self.server_url}/v1/chat/completions",
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"OpenAI API Error {response.status}: {error_text}")
                
                result = await response.json()
                
                # Извлекаем ответ из OpenAI формата
                if "choices" in result and len(result["choices"]) > 0:
                    response_text = result["choices"][0]["message"]["content"]
                else:
                    response_text = "Ошибка генерации ответа"
                
                # Метаданные
                metadata = {
                    "tokens_used": result.get("usage", {}).get("total_tokens", 0),
                    "model_data": {
                        "model": result.get("model", "unknown"),
                        "server_url": self.server_url
                    }
                }
                
                return response_text, metadata
                
        except Exception as e:
            raise Exception(f"Ошибка при обращении к OpenAI API: {str(e)}")
    
    async def generate_stream(
        self,
        messages: List[ChatMessage],
        character_config: CharacterConfig,
        temperature: float = 0.7,
        max_tokens: int = 200,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Генерирует ответ в потоковом режиме через OpenAI API."""
        
        if not self.session:
            raise RuntimeError("Сервис не инициализирован")
        
        # Формируем сообщения в формате OpenAI
        openai_messages = []
        
        # Добавляем system message
        system_prompt = self._format_system_prompt(character_config)
        openai_messages.append({
            "role": "system",
            "content": system_prompt
        })
        
        # Добавляем сообщения пользователя и ассистента
        for msg in messages:
            if msg.role == MessageRole.USER:
                openai_messages.append({
                    "role": "user",
                    "content": msg.content
                })
            elif msg.role == MessageRole.ASSISTANT:
                openai_messages.append({
                    "role": "assistant",
                    "content": msg.content
                })
        
        # Параметры для OpenAI API
        payload = {
            "model": settings.text_generation_webui_model.replace('.gguf',''),
            "messages": openai_messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": kwargs.get("top_p", 0.9),
            "top_k": kwargs.get("top_k", 40),
            "repetition_penalty": kwargs.get("repeat_penalty", 1.1),
            "stop": kwargs.get("stop", ["\n\n", "Human:", "Assistant:"]),
            "stream": True
        }
        
        try:
            async with self.session.post(
                f"{self.server_url}/v1/chat/completions",
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"OpenAI API Error {response.status}: {error_text}")
                
                async for line in response.content:
                    if line:
                        try:
                            line_text = line.decode('utf-8').strip()
                            if line_text.startswith('data: '):
                                data_str = line_text[6:]  # Убираем 'data: '
                                if data_str == '[DONE]':
                                    break
                                
                                data = json.loads(data_str)
                                if "choices" in data and len(data["choices"]) > 0:
                                    delta = data["choices"][0].get("delta", {})
                                    if "content" in delta:
                                        yield delta["content"]
                        except json.JSONDecodeError:
                            continue
                        except Exception as e:
                            logger.error(f"Ошибка обработки стрима: {e}")
                            break
                
        except Exception as e:
            raise Exception(f"Ошибка при стриминге: {str(e)}")
    
    def _format_system_prompt(self, character_config: CharacterConfig) -> str:
        """Форматирует system prompt с учетом персонажа."""
        # Собираем prompt из структурированных полей
        parts = []
        
        # Основная информация
        parts.append(f"Имя: {character_config.name}")
        if character_config.age:
            parts.append(f"Возраст: {character_config.age}")
        if character_config.profession:
            parts.append(f"Профессия: {character_config.profession}")
        parts.append(f"Личность: {character_config.personality}")
        if character_config.background:
            parts.append(f"Предыстория: {character_config.background}")
        if character_config.speaking_style:
            parts.append(f"Стиль речи: {character_config.speaking_style}")
        if character_config.interests:
            parts.append(f"Интересы: {', '.join(character_config.interests)}")
        if character_config.mood:
            parts.append(f"Настроение: {character_config.mood}")
        if character_config.behavior:
            parts.append(f"Поведение: {character_config.behavior}")
        if character_config.appearance:
            parts.append(f"Внешность: {character_config.appearance}")
        if character_config.voice:
            parts.append(f"Голос: {character_config.voice}")
        
        # Правила
        if character_config.rules:
            parts.append(f"\nПРАВИЛА:\n{character_config.rules}")
        
        # Контекст
        if character_config.context:
            parts.append(f"\nКОНТЕКСТ:\n{character_config.context}")
        
        # Дополнительные настройки
        additional_context = character_config.additional_context or {}
        max_length = additional_context.get('max_length', 300)
        parts.append(f"\nДлина ответа: до {max_length} символов.")
        
        return '\n'.join(parts)
    
    async def get_model_info(self) -> Dict[str, Any]:
        """Получает информацию о доступных моделях через OpenAI API."""
        if not self.session:
            raise RuntimeError("Сервис не инициализирован")
        
        try:
            async with self.session.get(f"{self.server_url}/v1/models") as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise Exception(f"Ошибка получения информации о моделях: {response.status}")
        except Exception as e:
            logger.error(f"Ошибка получения информации о моделях: {e}")
            raise


# Глобальный экземпляр сервиса
_textgen_webui_service: Optional[TextGenWebUIService] = None


async def get_textgen_webui_service() -> TextGenWebUIService:
    """Получает глобальный экземпляр сервиса text-generation-webui."""
    global _textgen_webui_service
    
    if _textgen_webui_service is None:
        _textgen_webui_service = TextGenWebUIService()
        await _textgen_webui_service.__aenter__()
    
    return _textgen_webui_service


async def close_textgen_webui_service():
    """Закрывает глобальный экземпляр сервиса."""
    global _textgen_webui_service
    
    if _textgen_webui_service:
        await _textgen_webui_service.__aexit__(None, None, None)
        _textgen_webui_service = None 