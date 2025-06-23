"""
Сервис для работы с Llama-моделью через llama-cpp-python (GGUF).
"""
import asyncio
import time
from typing import Optional, List, Dict, Any, Tuple
from pathlib import Path
from llama_cpp import Llama
from app.chat_bot.schemas.chat import ChatMessage, CharacterConfig
from app.chat_bot.config import chat_config
from app.utils.logger import logger

class LlamaCppChatService:
    def __init__(self) -> None:
        self.model: Optional[Llama] = None
        self.is_loaded: bool = False
        self._load_lock = asyncio.Lock()

    async def load_model(self) -> bool:
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
                self.model = Llama(
                    model_path=chat_config.MODEL_PATH,
                    n_ctx=chat_config.N_CTX,
                    n_threads=chat_config.N_THREADS,
                    n_batch=chat_config.N_BATCH,
                    n_gpu_layers=chat_config.N_GPU_LAYERS if chat_config.N_GPU_LAYERS >= 0 else 0,
                    verbose=False
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
            if message.role == "user":
                formatted_messages.append(f"<|user|>\n{message.content}</s>")
            elif message.role == "assistant":
                formatted_messages.append(f"<|assistant|>\n{message.content}</s>")
        formatted_messages.append("<|assistant|>\n")
        return "".join(formatted_messages)

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
        
        try:
            if self.model is None:
                raise RuntimeError("Модель не загружена")
            prompt = self._format_messages_for_model(messages, character_config)
            
            # Асинхронная генерация через executor
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: self.model(
                    prompt=prompt,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    top_p=top_p,
                    top_k=top_k,
                    repeat_penalty=repeat_penalty,
                    stop=["</s>", "<|user|>", "<|system|>"]
                )
            )
            
            # Обработка результата
            if isinstance(result, dict) and 'choices' in result and result['choices']:
                generated_text = result['choices'][0]['text'].strip()
            else:
                generated_text = str(result).strip()
            
            generation_time = time.time() - start_time
            
            metadata = {
                "tokens_used": result.get('usage', {}).get("total_tokens") if isinstance(result, dict) else None,
                "generation_time": generation_time,
                "model_info": {
                    "model_path": chat_config.MODEL_PATH,
                    "context_size": chat_config.N_CTX
                },
                "character_name": character_config.name
            }
            
            if chat_config.LOG_CHAT_RESPONSES:
                logger.info(f"Сгенерирован ответ: {generated_text[:100]}...")
            
            return generated_text, metadata
        except Exception as e:
            logger.error(f"Ошибка при генерации ответа: {str(e)}")
            raise RuntimeError(f"Ошибка генерации: {str(e)}")

    async def unload_model(self) -> None:
        if self.model is not None:
            del self.model
            self.model = None
            self.is_loaded = False
            logger.info("Модель выгружена из памяти")

llama_cpp_chat_service = LlamaCppChatService() 