"""
Сервис для взаимодействия с text-generation-webui API.
Оптимизирован для модели MythoMax L2 13B GGUF.
"""

import asyncio
import aiohttp
import json
import logging
from typing import Dict, List, Optional, Any, AsyncGenerator
from pydantic import BaseModel, Field
from app.chat_bot.config.chat_config import chat_config
from app.utils.logger import logger
from app.chat_bot.config.chat_config import ChatConfig

class TextGenWebUIService:
    """Сервис для работы с text-generation-webui API."""
    
    def __init__(self):
        """Инициализация сервиса."""
        self.base_url = chat_config.TEXTGEN_WEBUI_URL
        # Увеличиваем таймауты для предотвращения зависших соединений
        self.timeout = aiohttp.ClientTimeout(
            total=chat_config.TEXTGEN_WEBUI_TIMEOUT,
            connect=30,  # таймаут на подключение
            sock_read=60,  # таймаут на чтение
            sock_connect=30  # таймаут на создание сокета
        )
        self.model_name = chat_config.TEXTGEN_WEBUI_MODEL
        self._session: Optional[aiohttp.ClientSession] = None
        self._is_connected = False
        self._connector: Optional[aiohttp.TCPConnector] = None
        
    async def __aenter__(self):
        """Асинхронный контекстный менеджер - вход."""
        await self.connect()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Асинхронный контекстный менеджер - выход."""
        await self.disconnect()
        
    async def connect(self) -> None:
        """Устанавливает соединение с text-generation-webui."""
        if self._session is None:
            # Создаем TCP коннектор с ограничениями
            self._connector = aiohttp.TCPConnector(
                limit=100,  # максимальное количество соединений
                limit_per_host=30,  # максимальное количество соединений на хост
                ttl_dns_cache=300,  # TTL для DNS кэша
                use_dns_cache=True,  # использовать DNS кэш
                keepalive_timeout=30,  # таймаут keep-alive
                enable_cleanup_closed=True  # автоматическая очистка закрытых соединений
            )
            
            # Создаем сессию с улучшенными настройками
            self._session = aiohttp.ClientSession(
                timeout=self.timeout,
                connector=self._connector,
                connector_owner=False  # не закрывать коннектор при закрытии сессии
            )
            logger.info(f"🔌 Создана сессия для {self.base_url}")
            
    async def disconnect(self) -> None:
        """Закрывает соединение с text-generation-webui."""
        try:
            if self._session:
                await self._session.close()
                self._session = None
                logger.info("🔌 Сессия HTTP закрыта")
                
            if self._connector:
                await self._connector.close()
                self._connector = None
                logger.info("🔌 TCP коннектор закрыт")
                
            self._is_connected = False
            
        except Exception as e:
            logger.warning(f"⚠️ Ошибка при закрытии соединения: {e}")
        finally:
            self._session = None
            self._connector = None
            self._is_connected = False
            
    # ============================================================================
    # ⚠️  КРИТИЧЕСКИ ВАЖНЫЙ КОД - НЕ ИЗМЕНЯТЬ! ⚠️
    # ============================================================================
    # Этот метод отвечает за проверку подключения к text-generation-webui API.
    # Изменения здесь могут сломать всю систему подключения к LLM сервису.
    # 
    # КРИТИЧЕСКИЕ ЭЛЕМЕНТЫ:
    # - URL endpoint: /v1/models
    # - Проверка HTTP статуса 200
    # - Установка флага _is_connected
    # - Обработка ошибок JSON парсинга
    # ============================================================================
    
    async def check_connection(self) -> bool:
        """Проверяет доступность text-generation-webui API."""
        response = None
        try:
            if not self._session:
                await self.connect()
                
            logger.info(f"🔍 Проверяем соединение с {self.base_url}/v1/models")
            
            response = await self._session.get(f"{self.base_url}/v1/models")
            if response.status == 200:
                try:
                    result = await response.json()
                    models_count = len(result.get("data", []))
                    logger.info(f"✅ Соединение с text-generation-webui установлено. Доступно моделей: {models_count}")
                    self._is_connected = True
                    return True
                except Exception as json_err:
                    logger.warning(f"⚠️ Получен ответ 200, но не удалось распарсить JSON: {json_err}")
                    self._is_connected = True
                    return True
            else:
                error_text = await response.text()
                logger.warning(f"⚠️ text-generation-webui недоступен: HTTP {response.status}, ответ: {error_text}")
                self._is_connected = False
                return False
                
        except Exception as e:
            logger.error(f"❌ Ошибка подключения к text-generation-webui: {e}")
            self._is_connected = False
            return False
        finally:
            # Гарантированно закрываем response
            if response:
                try:
                    response.close()
                except Exception as e:
                    logger.warning(f"⚠️ Ошибка при закрытии response в check_connection: {e}")
    
    # ============================================================================
    # ✅ КРИТИЧЕСКИ ВАЖНЫЙ КОД ЗАВЕРШЕН
    # ============================================================================
            
    async def load_model(self, model_name: Optional[str] = None) -> bool:
        """Загружает модель в text-generation-webui."""
        response = None
        try:
            if not self._session:
                await self.connect()
                
            model_to_load = model_name or self.model_name
            payload = {"action": "load", "model_name": model_to_load}
            
            response = await self._session.post(f"{self.base_url}/v1/model/load", json=payload)
            if response.status == 200:
                result = await response.json()
                if result.get("result") == "success":
                    logger.info(f"✅ Модель {model_to_load} загружена успешно")
                    return True
                else:
                    logger.error(f"❌ Ошибка загрузки модели: {result}")
                    return False
            else:
                logger.error(f"❌ HTTP ошибка при загрузке модели: {response.status}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Ошибка загрузки модели: {e}")
            return False
        finally:
            # Гарантированно закрываем response
            if response:
                try:
                    response.close()
                except Exception as e:
                    logger.warning(f"⚠️ Ошибка при закрытии response в load_model: {e}")
            
    async def get_available_models(self) -> List[Dict[str, Any]]:
        """Получает список доступных моделей."""
        response = None
        try:
            if not self._session:
                await self.connect()
                
            response = await self._session.get(f"{self.base_url}/v1/models")
            if response.status == 200:
                data = await response.json()
                return data.get("data", [])
            else:
                logger.error(f"❌ HTTP ошибка при получении моделей: {response.status}")
                return []
                
        except Exception as e:
            logger.error(f"❌ Ошибка получения списка моделей: {e}")
            return []
        finally:
            # Гарантированно закрываем response
            if response:
                try:
                    response.close()
                except Exception as e:
                    logger.warning(f"⚠️ Ошибка при закрытии response в get_available_models: {e}")
            
    def build_mythomax_prompt(self, system_message: str, user_message: str, history: List[Dict[str, str]] = None) -> str:
        """
        Строит промпт в формате MythoMax для модели MythoMax L2 13B.
        
        Args:
            system_message: Системное сообщение/описание персонажа
            user_message: Сообщение пользователя
            history: История диалога (опционально)
            
        Returns:
            Сформированный промпт в формате MythoMax
        """
        try:
            # Начинаем с системного сообщения
            prompt = f"<|im_start|>system\n{system_message}<|im_end|>\n"
            
            # Добавляем историю диалога если есть
            if history:
                recent_history = history[-15:] if len(history) > 15 else history
                
                for msg in recent_history:
                    if isinstance(msg, dict):
                        role = msg.get("role", "user")
                        content = msg.get("content", "")
                    elif isinstance(msg, (tuple, list)) and len(msg) >= 2:
                        role = str(msg[0]) if msg[0] else "user"
                        content = str(msg[1]) if msg[1] else ""
                    else:
                        logger.warning(f"⚠️ Некорректный формат сообщения в истории: {msg}")
                        continue
                        
                    if role and content:
                        if role.lower() in ["user", "instruction"]:
                            prompt += f"<|im_start|>user\n{content}<|im_end|>\n"
                        elif role.lower() in ["assistant", "response"]:
                            prompt += f"<|im_start|>assistant\n{content}<|im_end|>\n"
                        
            # Добавляем текущее сообщение пользователя
            prompt += f"<|im_start|>user\n{user_message}<|im_end|>\n"
            
            # Завершаем промпт
            prompt += "<|im_start|>assistant\n"
            
            return prompt
            
        except Exception as e:
            logger.error(f"❌ Ошибка построения промпта: {e}")
            # Возвращаем простой fallback промпт в случае ошибки
            return f"<|im_start|>system\n{system_message}<|im_end|>\n<|im_start|>user\n{user_message}<|im_end|>\n<|im_start|>assistant\n"

    def build_character_prompt(
        self,
        character_data: Dict[str, Any],
        user_message: str,
        chat_history: List[Dict[str, str]] = None,
        chat_config: ChatConfig = None
    ) -> str:
        """
        Строит промпт для персонажа с учетом контекста и истории.
        
        Args:
            character_data: Данные персонажа
            user_message: Сообщение пользователя
            chat_history: История чата
            chat_config: Конфигурация чата
            
        Returns:
            Строка промпта для модели
        """
        if not character_data:
            return self._build_fallback_prompt(user_message, chat_config)
            
        # Получаем базовые данные персонажа
        system_prompt = character_data.get("system_prompt", "")
        instructions = character_data.get("instructions", "")
        response_format = character_data.get("response_format", "")
        
        # Строим базовый системный промпт
        system_parts = []
        if system_prompt:
            system_parts.append(system_prompt)
        if instructions:
            system_parts.append("\n" + instructions)
        if response_format:
            system_parts.append("\n" + response_format)
            
        system_message = "\n".join(system_parts)
        
        # Строим контекст из истории
        context_text = ""
        if chat_history:
            recent_history = chat_history[-15:] if len(chat_history) > 15 else chat_history
            context_parts = []
            for msg in recent_history:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                if role == "user":
                    context_parts.append(f"User: {content}")
                elif role == "assistant":
                    context_parts.append(f"Assistant: {content}")
            if context_parts:
                context_text = "\n".join(context_parts) + "\n\n"
        
        # Возвращаем финальный промпт
        return f"{system_message}\n\n{context_text}{user_message}\n\n### Response:\n"

    def _build_fallback_prompt(self, user_message: str, chat_config: ChatConfig = None) -> str:
        """
        Строит fallback промпт для случаев, когда данные персонажа недоступны.
        
        Args:
            user_message: Сообщение пользователя
            chat_config: Конфигурация чата
            
        Returns:
            Fallback промпт
        """
        fallback_prompt = "Ты дружелюбный и полезный ассистент. Отвечай от первого лица."
        fallback_prompt += "\n\nAlways respond directly to what the user just said."
        fallback_prompt += "\nUse context from previous messages when available."
        
        return f"{fallback_prompt}\n\n{user_message}\n\n### Response:\n"

    async def generate_text(
        self, 
        prompt: str, 
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        top_k: Optional[int] = None,
        repeat_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None
    ) -> Optional[str]:
        """
        Генерирует текст через text-generation-webui API.
        
        Args:
            prompt: Промпт для генерации
            max_tokens: Максимальное количество токенов
            temperature: Температура генерации
            top_p: Top-p параметр
            top_k: Top-k параметр
            repeat_penalty: Штраф за повторения
            presence_penalty: Presence penalty
            
        Returns:
            Сгенерированный текст или None при ошибке
        """
        response = None
        try:
            if not self._session:
                await self.connect()
                
            # Проверяем, что промпт не пустой
            if not prompt or not prompt.strip():
                logger.error("❌ Пустой промпт для генерации")
                return None
                
            # Настройки будут использованы в OpenAI-совместимом API
            
            # Используем OpenAI-совместимый API с ВСЕМИ настройками из конфигурации
            openai_payload = {
                "model": self.model_name,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tokens or chat_config.DEFAULT_MAX_TOKENS,
                "temperature": temperature or chat_config.DEFAULT_TEMPERATURE,
                "top_p": top_p or chat_config.DEFAULT_TOP_P,
                "top_k": top_k or chat_config.DEFAULT_TOP_K,
                "presence_penalty": presence_penalty or chat_config.DEFAULT_PRESENCE_PENALTY,
                "frequency_penalty": repeat_penalty or chat_config.DEFAULT_REPEAT_PENALTY,
                "stop": chat_config.DEFAULT_STOP_TOKENS,  # Стоп-токены для остановки
                "stream": False,
                "seed": chat_config.SEED if chat_config.SEED != -1 else 42,  # Seed для генерации
                
                # Аппаратные параметры из конфигурации
                "n_ctx": chat_config.N_CTX,
                "n_gpu_layers": chat_config.N_GPU_LAYERS,
                "n_threads": chat_config.N_THREADS,
                "n_threads_batch": chat_config.N_THREADS_BATCH,
                "n_batch": chat_config.N_BATCH,
                "f16_kv": chat_config.F16_KV,
                "mul_mat_q": chat_config.MUL_MAT_Q,
                "use_mmap": chat_config.USE_MMAP,
                "use_mlock": chat_config.USE_MLOCK,
                "verbose": chat_config.VERBOSE,
                "offload_kqv": chat_config.OFFLOAD_KQV,
                
                # Параметры скорости/памяти
                "n_keep": chat_config.N_KEEP,
                "n_draft": chat_config.N_DRAFT,
                "n_chunks": chat_config.N_CHUNKS,
                "n_parallel": chat_config.N_PARALLEL,
                "vocab_only": chat_config.VOCAB_ONLY,
                
                # Дополнительные параметры
                "rope_scaling": chat_config.ROPE_SCALING,
                "ftype": chat_config.FTYPE,
                
                # Параметры качества и умности
                "smartness": chat_config.SMARTNESS,
                "dynamic_sampling": chat_config.DYNAMIC_SAMPLING,
                "temp_variance": chat_config.TEMP_VARIANCE,
                "top_p_variance": chat_config.TOP_P_VARIANCE,
                "occasional_beam_prob": chat_config.OCCASIONAL_BEAM_PROB,
                "enable_cot": chat_config.ENABLE_COT,
                "few_shot_examples": chat_config.FEW_SHOT_EXAMPLES,
                
                # Параметры контекста и длины
                "max_history_length": chat_config.MAX_HISTORY_LENGTH,
                "max_message_length": chat_config.MAX_MESSAGE_LENGTH,
                "max_response_length": chat_config.MAX_RESPONSE_LENGTH,
                "enforce_min_tokens": chat_config.ENFORCE_MIN_TOKENS,
                "min_new_tokens": chat_config.MIN_NEW_TOKENS,
                "ban_eos_token": chat_config.BAN_EOS_TOKEN,
                
                # Параметры безопасности и фильтрации
                "enable_content_filter": chat_config.ENABLE_CONTENT_FILTER,
                "forbidden_words": chat_config.FORBIDDEN_WORDS,
                
                # Параметры очистки и стриминга
                "sanitize_output": chat_config.SANITIZE_OUTPUT,
                "streaming_delay_ms": chat_config.STREAMING_DELAY_MS,
                
                # Дополнительные параметры
                "embedding": chat_config.EMBEDDING
            }
            
            logger.info(f"🚀 Отправляем запрос на генерацию текста (промпт: {len(prompt)} символов)")
            
            response = await self._session.post(f"{self.base_url}/v1/chat/completions", json=openai_payload)
            if response.status == 200:
                result = await response.json()
                generated_text = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                
                if generated_text:
                    logger.info(f"✅ Текст сгенерирован успешно ({len(generated_text)} символов)")
                    return generated_text
                else:
                    logger.warning("⚠️ Получен пустой ответ от API")
                    return None
            else:
                error_text = await response.text()
                logger.error(f"❌ HTTP ошибка при генерации: {response.status}, ответ: {error_text}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Ошибка генерации текста: {e}")
            return None
        finally:
            # Гарантированно закрываем response
            if response:
                try:
                    response.close()
                except Exception as e:
                    logger.warning(f"⚠️ Ошибка при закрытии response в generate_text: {e}")
            
    # ============================================================================
    # ⚠️  КРИТИЧЕСКИ ВАЖНЫЙ КОД - НЕ ИЗМЕНЯТЬ! ⚠️
    # ============================================================================
    # Этот метод отвечает за streaming генерацию текста через text-generation-webui API.
    # Изменения здесь могут сломать всю систему streaming чата.
    # 
    # КРИТИЧЕСКИЕ ЭЛЕМЕНТЫ:
    # - Сигнатура метода (параметры должны точно совпадать)
    # - OpenAI-совместимый payload формат
    # - Обработка streaming ответа
    # - Парсинг JSON чанков
    # - НЕ дублировать параметр "stream": True
    # ============================================================================
    
    async def generate_text_stream(
        self, 
        prompt: str, 
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        top_k: Optional[int] = None,
        repeat_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None
    ) -> AsyncGenerator[str, None]:
        """
        Генерирует текст потоком через text-generation-webui API.
        
        Args:
            prompt: Промпт для генерации
            max_tokens: Максимальное количество токенов
            temperature: Температура генерации
            top_p: Top-p параметр
            top_k: Top-k параметр
            repeat_penalty: Штраф за повторения
            presence_penalty: Presence penalty
            
        Yields:
            Части сгенерированного текста
        """
        try:
            if not self._session:
                await self.connect()
                
            # Проверяем, что промпт не пустой
            if not prompt or not prompt.strip():
                logger.error("❌ Пустой промпт для генерации")
                return
                
            # Настройки будут использованы в OpenAI-совместимом API
            
            # Используем OpenAI-совместимый API для стриминга с ВСЕМИ настройками из конфигурации
            openai_payload = {
                "model": self.model_name,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tokens or chat_config.DEFAULT_MAX_TOKENS,
                "temperature": temperature or chat_config.DEFAULT_TEMPERATURE,
                "top_p": top_p or chat_config.DEFAULT_TOP_P,
                "top_k": top_k or chat_config.DEFAULT_TOP_K,
                "presence_penalty": presence_penalty or chat_config.DEFAULT_PRESENCE_PENALTY,
                "frequency_penalty": repeat_penalty or chat_config.DEFAULT_REPEAT_PENALTY,
                "stop": chat_config.DEFAULT_STOP_TOKENS,  # Стоп-токены для остановки
                "stream": True,
                "seed": chat_config.SEED if chat_config.SEED != -1 else 42,  # Seed для генерации
                
                # Аппаратные параметры из конфигурации
                "n_ctx": chat_config.N_CTX,
                "n_gpu_layers": chat_config.N_GPU_LAYERS,
                "n_threads": chat_config.N_THREADS,
                "n_threads_batch": chat_config.N_THREADS_BATCH,
                "n_batch": chat_config.N_BATCH,
                "f16_kv": chat_config.F16_KV,
                "mul_mat_q": chat_config.MUL_MAT_Q,
                "use_mmap": chat_config.USE_MMAP,
                "use_mlock": chat_config.USE_MLOCK,
                "verbose": chat_config.VERBOSE,
                "offload_kqv": chat_config.OFFLOAD_KQV,
                
                # Параметры скорости/памяти
                "n_keep": chat_config.N_KEEP,
                "n_draft": chat_config.N_DRAFT,
                "n_chunks": chat_config.N_CHUNKS,
                "n_parallel": chat_config.N_PARALLEL,
                "vocab_only": chat_config.VOCAB_ONLY,
                
                # Дополнительные параметры
                "rope_scaling": chat_config.ROPE_SCALING,
                "ftype": chat_config.FTYPE,
                
                # Параметры качества и умности
                "smartness": chat_config.SMARTNESS,
                "dynamic_sampling": chat_config.DYNAMIC_SAMPLING,
                "temp_variance": chat_config.TEMP_VARIANCE,
                "top_p_variance": chat_config.TOP_P_VARIANCE,
                "occasional_beam_prob": chat_config.OCCASIONAL_BEAM_PROB,
                "enable_cot": chat_config.ENABLE_COT,
                "few_shot_examples": chat_config.FEW_SHOT_EXAMPLES,
                
                # Параметры контекста и длины
                "max_history_length": chat_config.MAX_HISTORY_LENGTH,
                "max_message_length": chat_config.MAX_MESSAGE_LENGTH,
                "max_response_length": chat_config.MAX_RESPONSE_LENGTH,
                "enforce_min_tokens": chat_config.ENFORCE_MIN_TOKENS,
                "min_new_tokens": chat_config.MIN_NEW_TOKENS,
                "ban_eos_token": chat_config.BAN_EOS_TOKEN,
                
                # Параметры безопасности и фильтрации
                "enable_content_filter": chat_config.ENABLE_CONTENT_FILTER,
                "forbidden_words": chat_config.FORBIDDEN_WORDS,
                
                # Параметры очистки и стриминга
                "sanitize_output": chat_config.SANITIZE_OUTPUT,
                "streaming_delay_ms": chat_config.STREAMING_DELAY_MS,
                
                # Дополнительные параметры
                "embedding": chat_config.EMBEDDING
            }
            
            logger.info(f"🚀 Отправляем запрос на генерацию текста (промпт: {len(prompt)} символов)")
            
            # Используем try-finally для гарантированного закрытия ресурсов
            response = None
            try:
                response = await self._session.post(f"{self.base_url}/v1/chat/completions", json=openai_payload)
                
                if response.status == 200:
                    logger.info("✅ Получен ответ от text-generation-webui, начинаем обработку стрима")
                    buffer = ""
                    
                    async for line in response.content:
                        if line:
                            try:
                                # Декодируем и добавляем к буферу
                                buffer += line.decode('utf-8')
                                
                                # Обрабатываем полные строки
                                lines = buffer.split('\n')
                                buffer = lines.pop() or ""  # Оставляем неполную строку в буфере
                                
                                for line_text in lines:
                                    line_text = line_text.strip()
                                    if not line_text or not line_text.startswith('data: '):
                                        continue
                                        
                                    data_str = line_text[6:]  # Убираем 'data: '
                                    if data_str == '[DONE]':
                                        logger.info("🏁 Получен сигнал завершения стрима")
                                        return
                                        
                                    try:
                                        data = json.loads(data_str)
                                        if 'choices' in data and len(data['choices']) > 0:
                                            delta = data['choices'][0].get('delta', {})
                                            if 'content' in delta and delta['content']:
                                                # НЕМЕДЛЕННО отдаем каждый чанк
                                                yield delta['content']
                                                
                                    except json.JSONDecodeError as json_err:
                                        logger.warning(f"⚠️ Ошибка парсинга JSON в стриме: {json_err}, данные: {data_str}")
                                        continue
                                        
                            except Exception as e:
                                logger.warning(f"⚠️ Ошибка обработки стрима: {e}")
                                continue
                else:
                    error_text = await response.text()
                    logger.error(f"❌ HTTP ошибка при потоковой генерации: {response.status}, ответ: {error_text}")
                    
            finally:
                # Гарантированно закрываем response
                if response:
                    try:
                        response.close()
                    except Exception as e:
                        logger.warning(f"⚠️ Ошибка при закрытии response: {e}")
                        
        except Exception as e:
            logger.error(f"❌ Ошибка потоковой генерации текста: {e}")
            # Возвращаем сообщение об ошибке
            yield f"Извините, произошла ошибка при генерации текста: {str(e)}"
    
    # ============================================================================
    # ✅ КРИТИЧЕСКИ ВАЖНЫЙ КОД ЗАВЕРШЕН
    # ============================================================================
            
    async def get_model_status(self) -> Dict[str, Any]:
        """Получает статус текущей модели."""
        response = None
        try:
            if not self._session:
                await self.connect()
                
            response = await self._session.get(f"{self.base_url}/v1/model")
            if response.status == 200:
                return await response.json()
            else:
                logger.error(f"❌ HTTP ошибка при получении статуса модели: {response.status}")
                return {}
                
        except Exception as e:
            logger.error(f"❌ Ошибка получения статуса модели: {e}")
            return {}
        finally:
            # Гарантированно закрываем response
            if response:
                try:
                    response.close()
                except Exception as e:
                    logger.warning(f"⚠️ Ошибка при закрытии response в get_model_status: {e}")
            
    @property
    def is_connected(self) -> bool:
        """Проверяет, установлено ли соединение."""
        return self._is_connected
        
    @property
    def is_available(self) -> bool:
        """Проверяет доступность сервиса."""
        return self._is_connected and self._session is not None
    
    def get_config_for_bat_file(self) -> Dict[str, Any]:
        """
        Возвращает ВСЕ настройки конфигурации для использования в bat-файлах.
        Теперь все параметры из chat_config.py используются в API!
        """
        return {
            # Аппаратные параметры
            "n_ctx": chat_config.N_CTX,
            "n_gpu_layers": chat_config.N_GPU_LAYERS,
            "n_threads": chat_config.N_THREADS,
            "n_threads_batch": chat_config.N_THREADS_BATCH,
            "n_batch": chat_config.N_BATCH,
            "f16_kv": chat_config.F16_KV,
            "mul_mat_q": chat_config.MUL_MAT_Q,
            "use_mmap": chat_config.USE_MMAP,
            "use_mlock": chat_config.USE_MLOCK,
            "verbose": chat_config.VERBOSE,
            "offload_kqv": chat_config.OFFLOAD_KQV,
            
            # Параметры скорости/памяти
            "n_keep": chat_config.N_KEEP,
            "n_draft": chat_config.N_DRAFT,
            "n_chunks": chat_config.N_CHUNKS,
            "n_parallel": chat_config.N_PARALLEL,
            "vocab_only": chat_config.VOCAB_ONLY,
            
            # Дополнительные параметры
            "rope_scaling": chat_config.ROPE_SCALING,
            "ftype": chat_config.FTYPE,
            
            # Параметры качества и умности
            "smartness": chat_config.SMARTNESS,
            "dynamic_sampling": chat_config.DYNAMIC_SAMPLING,
            "temp_variance": chat_config.TEMP_VARIANCE,
            "top_p_variance": chat_config.TOP_P_VARIANCE,
            "occasional_beam_prob": chat_config.OCCASIONAL_BEAM_PROB,
            "enable_cot": chat_config.ENABLE_COT,
            "few_shot_examples": chat_config.FEW_SHOT_EXAMPLES,
            
            # Параметры контекста и длины
            "max_history_length": chat_config.MAX_HISTORY_LENGTH,
            "max_message_length": chat_config.MAX_MESSAGE_LENGTH,
            "max_response_length": chat_config.MAX_RESPONSE_LENGTH,
            "enforce_min_tokens": chat_config.ENFORCE_MIN_TOKENS,
            "min_new_tokens": chat_config.MIN_NEW_TOKENS,
            "ban_eos_token": chat_config.BAN_EOS_TOKEN,
            
            # Параметры безопасности и фильтрации
            "enable_content_filter": chat_config.ENABLE_CONTENT_FILTER,
            "forbidden_words": chat_config.FORBIDDEN_WORDS,
            
            # Параметры очистки и стриминга
            "sanitize_output": chat_config.SANITIZE_OUTPUT,
            "streaming_delay_ms": chat_config.STREAMING_DELAY_MS,
            
            # Дополнительные параметры
            "embedding": chat_config.EMBEDDING,
            "seed": chat_config.SEED if chat_config.SEED != -1 else None
        }
        
    # ============================================================================
    # ⚠️  КРИТИЧЕСКИ ВАЖНЫЙ КОД - НЕ ИЗМЕНЯТЬ! ⚠️
    # ============================================================================
    # Этот метод является алиасом для generate_text_stream.
    # Изменения здесь могут сломать обратную совместимость.
    # 
    # КРИТИЧЕСКИЕ ЭЛЕМЕНТЫ:
    # - Должен точно передавать все аргументы в generate_text_stream
    # - НЕ изменять логику - только проксирование
    # - Сохранять сигнатуру AsyncGenerator[str, None]
    # ============================================================================
    
    async def generate_stream(self, *args, **kwargs) -> AsyncGenerator[str, None]:
        """
        Алиас для generate_text_stream для обратной совместимости.
        
        Args:
            *args: Аргументы для generate_text_stream
            **kwargs: Ключевые аргументы для generate_text_stream
            
        Yields:
            Части сгенерированного текста
        """
        async for chunk in self.generate_text_stream(*args, **kwargs):
            yield chunk
    
    # ============================================================================
    # ✅ КРИТИЧЕСКИ ВАЖНЫЙ КОД ЗАВЕРШЕН
    # ============================================================================

# Создаем глобальный экземпляр сервиса
textgen_webui_service = TextGenWebUIService()
