"""
Сервис для работы с Llama (через llama-cpp-python) в чат-боте.
"""
import asyncio
import time
import hashlib
import json
from typing import List, Optional, Dict, Any, Tuple
from pathlib import Path
import logging

import llama_cpp
from app.chat_bot.schemas.chat import ChatMessage, CharacterConfig, MessageRole
from app.chat_bot.config import chat_config
from app.utils.logger import logger


class LlamaChatService:
    """
    Сервис для работы с Llama моделью через llama-cpp-python в чат-боте.
    """
    def __init__(self) -> None:
        self.model: Optional[llama_cpp.Llama] = None
        self.is_loaded: bool = False
        self.cache: Dict[str, str] = {}
        self._load_lock = asyncio.Lock()

    async def load_model(self) -> bool:
        """
        Загружает модель Llama через llama-cpp-python.
        Returns:
            bool: True если модель успешно загружена
        """
        if self.is_loaded and self.model is not None:
            return True
        async with self._load_lock:
            if self.is_loaded and self.model is not None:
                return True
            try:
                logger.info(f"Загрузка модели через llama-cpp-python из: {chat_config.MODEL_PATH}")
                if not Path(chat_config.MODEL_PATH).exists():
                    logger.error(f"Файл модели не найден: {chat_config.MODEL_PATH}")
                    return False
                
                # Используем llama-cpp-python вместо ctransformers
                self.model = llama_cpp.Llama(
                    model_path=chat_config.MODEL_PATH,
                    n_ctx=chat_config.N_CTX,
                    n_threads=chat_config.N_THREADS,
                    n_batch=chat_config.N_BATCH,
                    n_gpu_layers=chat_config.N_GPU_LAYERS  # Используем GPU слои
                )
                
                self.is_loaded = True
                logger.info("Модель успешно загружена через llama-cpp-python")
                return True
                
            except Exception as e:
                logger.error(f"Ошибка при загрузке модели: {str(e)}")
                self.is_loaded = False
                self.model = None
                return False

    def _create_system_prompt(self, character_config: CharacterConfig) -> str:
        """
        Создает системный промпт на основе конфигурации персонажа.
        """
        prompt_parts = [
            f"Ты — {character_config.name}. {character_config.personality}"
        ]
        if character_config.background:
            prompt_parts.append(f"Твоя предыстория: {character_config.background}")
        if character_config.speaking_style:
            prompt_parts.append(f"Твой стиль речи: {character_config.speaking_style}")
        if character_config.interests:
            interests_str = ", ".join(character_config.interests)
            prompt_parts.append(f"Твои интересы: {interests_str}")
        if character_config.mood:
            prompt_parts.append(f"Твое текущее настроение: {character_config.mood}")

        prompt_parts.extend([
            "Отвечай от первого лица, как будто ты действительно этот персонаж.",
            "Будь естественным и дружелюбным в общении.",
            "Не используй формальные фразы типа 'Как ИИ-ассистент'.",
            "Отвечай на русском языке."
        ])
        return "\n".join(prompt_parts)

    def _format_messages_for_model(self, messages: List[ChatMessage], character_config: CharacterConfig) -> str:
        system_prompt = self._create_system_prompt(character_config)
        formatted_messages = [f"<|system|>\n{system_prompt}</s>"]
        for message in messages:
            if message.role == MessageRole.USER:
                formatted_messages.append(f"<|user|>\n{message.content}</s>")
            elif message.role == MessageRole.ASSISTANT:
                formatted_messages.append(f"<|assistant|>\n{message.content}</s>")
        formatted_messages.append("<|assistant|>\n")
        return "".join(formatted_messages)

    def _create_cache_key(self, messages: List[ChatMessage], character_config: CharacterConfig, generation_params: Dict[str, Any]) -> str:
        data = {
            "messages": [msg.dict() for msg in messages],
            "character": character_config.dict(),
            "params": generation_params
        }
        data_str = json.dumps(data, sort_keys=True, ensure_ascii=False)
        return hashlib.md5(data_str.encode()).hexdigest()

    def _filter_content(self, text: str) -> str:
        if not chat_config.ENABLE_CONTENT_FILTER:
            return text
        filtered_text = text
        for word in chat_config.FORBIDDEN_WORDS:
            filtered_text = filtered_text.replace(word, "*" * len(word))
        return filtered_text

    async def generate_response(
        self,
        messages: List[ChatMessage],
        character_config: CharacterConfig,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        top_k: Optional[int] = None,
        repeat_penalty: Optional[float] = None
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Генерирует ответ от модели через llama-cpp-python.
        Returns:
            Tuple[str, Dict[str, Any]]: Ответ и метаданные
        """
        start_time = time.time()
        if not await self.load_model():
            raise RuntimeError("Не удалось загрузить модель")
        
        max_tokens = max_tokens or chat_config.DEFAULT_MAX_TOKENS
        temperature = temperature or chat_config.DEFAULT_TEMPERATURE
        top_p = top_p or chat_config.DEFAULT_TOP_P
        top_k = top_k or chat_config.DEFAULT_TOP_K
        repeat_penalty = repeat_penalty or chat_config.DEFAULT_REPEAT_PENALTY
        
        if len(messages) > chat_config.MAX_HISTORY_LENGTH:
            messages = messages[-chat_config.MAX_HISTORY_LENGTH:]
        
        generation_params = {
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "top_k": top_k,
            "repeat_penalty": repeat_penalty
        }
        
        cache_key = self._create_cache_key(messages, character_config, generation_params)
        if chat_config.ENABLE_CACHE and cache_key in self.cache:
            logger.info("Ответ найден в кэше")
            return self.cache[cache_key], {"cached": True, "generation_time": 0.0}
        
        if chat_config.LOG_CHAT_REQUESTS:
            logger.info(f"Генерация ответа для персонажа: {character_config.name}")
        
        try:
            if self.model is None:
                raise RuntimeError("Модель не загружена")
            
            # Используем llama-cpp-python API
            prompt = self._format_messages_for_model(messages, character_config)
            
            response = self.model(
                prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                top_k=top_k,
                repeat_penalty=repeat_penalty,
                stop=["</s>", "<|user|>", "<|system|>"]
            )
            
            # Получаем текст ответа из структуры ответа
            if isinstance(response, dict) and "choices" in response:
                generated_text = response["choices"][0]["text"].strip()
                tokens_used = response.get("usage", {}).get("total_tokens")
            else:
                # Fallback для других форматов ответа
                generated_text = str(response).strip()
                tokens_used = None
            
            filtered_text = self._filter_content(generated_text)
            generation_time = time.time() - start_time
            
            metadata = {
                "tokens_used": tokens_used,
                "generation_time": generation_time,
                "model": "llama-cpp-python",
                "character": character_config.name
            }
            
            if chat_config.ENABLE_CACHE:
                self.cache[cache_key] = filtered_text
                # Ограничиваем размер кэша (используем значение по умолчанию)
                max_cache_size = getattr(chat_config, 'MAX_CACHE_SIZE', 1000)
                if len(self.cache) > max_cache_size:
                    oldest_key = next(iter(self.cache))
                    del self.cache[oldest_key]
            
            return filtered_text, metadata
            
        except Exception as e:
            logger.error(f"Ошибка при генерации ответа: {str(e)}")
            raise RuntimeError(f"Ошибка генерации: {str(e)}")

    async def unload_model(self) -> None:
        """
        Выгружает модель из памяти.
        """
        if self.model is not None:
            del self.model
            self.model = None
        self.is_loaded = False
        self.cache.clear()
        logger.info("Модель выгружена из памяти")

    def get_model_info(self) -> Dict[str, Any]:
        """
        Возвращает информацию о загруженной модели.
        """
        if not self.is_loaded or self.model is None:
            return {"status": "not_loaded"}
        
        return {
            "status": "loaded",
            "model_path": chat_config.MODEL_PATH,
            "context_length": chat_config.N_CTX,
            "threads": chat_config.N_THREADS,
            "cache_size": len(self.cache)
        }

llama_chat_service = LlamaChatService() 