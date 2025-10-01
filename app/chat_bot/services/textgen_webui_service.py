"""
Сервис для взаимодействия с text-generation-webui API.
Оптимизирован для модели MythoMax-L2-13B-GGUF.
Использует Alpaca prompt template. Специализированная модель для ролевых игр.
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
        # ОПТИМИЗИРОВАННЫЕ таймауты для максимальной скорости
        self.timeout = aiohttp.ClientTimeout(
            total=300,  # Увеличено до 5 минут для длинных ответов
            connect=10,  # Больше времени на подключение
            sock_read=120,  # Увеличено до 2 минут на чтение
            sock_connect=10
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
            # БЫСТРЫЙ TCP коннектор для локального API
            self._connector = aiohttp.TCPConnector(
                limit=10,  # УМЕНЬШЕНО - для локального API не нужно много соединений
                limit_per_host=5,  # УМЕНЬШЕНО для localhost
                ttl_dns_cache=60,  # УМЕНЬШЕНО - localhost не меняется
                use_dns_cache=False,  # ОТКЛЮЧЕНО для localhost
                enable_cleanup_closed=True,
                force_close=True  # Принудительное закрытие (без keepalive_timeout!)
            )
            
            # Создаем сессию с улучшенными настройками
            self._session = aiohttp.ClientSession(
                timeout=self.timeout,
                connector=self._connector,
                connector_owner=True  # автоматически закрывать коннектор при закрытии сессии
            )
            logger.info(f"🔌 Создана сессия для {self.base_url}")
            
    async def disconnect(self) -> None:
        """Закрывает соединение с text-generation-webui."""
        try:
            if self._session and not self._session.closed:
                await self._session.close()
                # Дождемся полного закрытия соединений
                await asyncio.sleep(0.1)
                logger.info("🔌 Сессия HTTP закрыта")
                
            # Коннектор закроется автоматически с сессией (connector_owner=True)
            self._is_connected = False
            
        except Exception as e:
            logger.warning(f"[WARNING] Ошибка при закрытии соединения: {e}")
        finally:
            self._session = None
            self._connector = None
            self._is_connected = False
            
    # ============================================================================
    # [WARNING]  КРИТИЧЕСКИ ВАЖНЫЙ КОД - НЕ ИЗМЕНЯТЬ! [WARNING]
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
                    logger.info(f"[OK] Соединение с text-generation-webui установлено. Доступно моделей: {models_count}")
                    self._is_connected = True
                    return True
                except Exception as json_err:
                    logger.warning(f"[WARNING] Получен ответ 200, но не удалось распарсить JSON: {json_err}")
                    self._is_connected = True
                    return True
            else:
                error_text = await response.text()
                logger.warning(f"[WARNING] text-generation-webui недоступен: HTTP {response.status}, ответ: {error_text}")
                self._is_connected = False
                return False
                
        except Exception as e:
            logger.error(f"[ERROR] Ошибка подключения к text-generation-webui: {e}")
            self._is_connected = False
            return False
        finally:
            # Гарантированно закрываем response
            if response:
                try:
                    response.close()
                except Exception as e:
                    logger.warning(f"[WARNING] Ошибка при закрытии response в check_connection: {e}")
    
    # ============================================================================
    # [OK] КРИТИЧЕСКИ ВАЖНЫЙ КОД ЗАВЕРШЕН
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
                    logger.info(f"[OK] Модель {model_to_load} загружена успешно")
                    return True
                else:
                    logger.error(f"[ERROR] Ошибка загрузки модели: {result}")
                    return False
            else:
                logger.error(f"[ERROR] HTTP ошибка при загрузке модели: {response.status}")
                return False
                
        except Exception as e:
            logger.error(f"[ERROR] Ошибка загрузки модели: {e}")
            return False
        finally:
            # Гарантированно закрываем response
            if response:
                try:
                    response.close()
                except Exception as e:
                    logger.warning(f"[WARNING] Ошибка при закрытии response в load_model: {e}")
            
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
                logger.error(f"[ERROR] HTTP ошибка при получении моделей: {response.status}")
                return []
                
        except Exception as e:
            logger.error(f"[ERROR] Ошибка получения списка моделей: {e}")
            return []
        finally:
            # Гарантированно закрываем response
            if response:
                try:
                    response.close()
                except Exception as e:
                    logger.warning(f"[WARNING] Ошибка при закрытии response в get_available_models: {e}")
            
    def build_alpaca_prompt(self, system_message: str, user_message: str, history: List[Dict[str, str]] = None) -> str:
        """
        Строит промпт в формате Alpaca для модели MythoMax-L2-13B.
        
        Args:
            system_message: Системное сообщение/описание персонажа
            user_message: Сообщение пользователя
            history: История диалога (опционально)
            
        Returns:
            Сформированный промпт в формате Alpaca
        """
        try:
            # Начинаем с системного сообщения в формате Alpaca
            prompt = f"{system_message}\n\n"
            
            # Добавляем историю диалога если есть
            if history:
                recent_history = history[-20:] if len(history) > 20 else history
                
                for i, msg in enumerate(recent_history):
                    if isinstance(msg, dict):
                        role = msg.get("role", "user")
                        content = msg.get("content", "")
                    elif isinstance(msg, (tuple, list)) and len(msg) >= 2:
                        role = str(msg[0]) if msg[0] else "user"
                        content = str(msg[1]) if msg[1] else ""
                    else:
                        logger.warning(f"[WARNING] Некорректный формат сообщения в истории: {msg}")
                        continue
                        
                    if role and content:
                        if role.lower() in ["user"]:
                            prompt += f"### Instruction:\n{content}\n\n"
                        elif role.lower() in ["assistant"]:
                            prompt += f"### Response:\n{content}\n\n"
                        
            # Добавляем текущее сообщение пользователя
            prompt += f"### Instruction:\n{user_message}\n\n"
            
            # Завершаем промпт для генерации ответа
            prompt += "### Response:\n"
            
            return prompt
            
        except Exception as e:
            logger.error(f"[ERROR] Ошибка построения промпта: {e}")
            # Возвращаем простой fallback промпт в случае ошибки
            return f"{system_message}\n\n### Instruction:\n{user_message}\n\n### Response:\n"

    def build_character_prompt(
        self,
        character_data: Dict[str, Any],
        user_message: str,
        chat_history: List[Dict[str, str]] = None,
        history: List[Dict[str, str]] = None,
        chat_config: ChatConfig = None
    ) -> str:
        """
        Строит промпт для персонажа в формате Alpaca для MythoMax-L2-13B.
        Оптимизировано для ролевых игр и творческого письма.
        """
        if not character_data:
            return self._build_fallback_prompt(user_message, chat_config)
            
        character_prompt = character_data.get("prompt", "")
        if not character_prompt:
            return self._build_fallback_prompt(user_message, chat_config)
        
        # Проверяем, содержит ли промпт placeholder для сообщения
        if "{user_message}" in character_prompt:
            # Если промпт уже содержит placeholder, заменяем его
            return character_prompt.replace("{user_message}", user_message)
        
        # Если нет placeholder, строим стандартный Alpaca промпт
        prompt = f"{character_prompt}\n\n"
        
        # История диалога для MythoMax
        history_to_use = history or chat_history
        if history_to_use:
            recent_history = history_to_use[-20:]  # Оптимально для 8192 контекста
            for i, msg in enumerate(recent_history):
                role = msg.get("role", "user")
                content = msg.get("content", "")[:1000]  # Контролируемая длина для 13B модели
                if content.strip():
                    if role == "user":
                        prompt += f"### Instruction:\n{content}\n\n"
                    elif role == "assistant":
                        prompt += f"### Response:\n{content}\n\n"
        
        # Добавляем текущее сообщение в Alpaca формате
        prompt += f"### Instruction:\n{user_message}\n\n"
        
        # Завершаем промпт для генерации ответа
        prompt += "### Response:\n"
        
        return prompt

    def _clean_generation_artifacts(self, text: str) -> str:
        """
        Очищает текст от артефактов генерации и предотвращает выход из роли.
        
        Args:
            text: Сырой текст от модели
            
        Returns:
            Очищенный текст
        """
        import re
        
        # ИСПРАВЛЕНО: Смягченная пост-обработка - сохраняем естественные завершения
        
        # КРИТИЧЕСКИ ВАЖНО: Удаляем только HTML-ссылки и теги, но сохраняем естественную пунктуацию
        text = re.sub(r'<a\s+href\s*=\s*[^>]*>.*?</a>', '', text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r'<[^>]+>', '', text)  # Удаляем все HTML теги
        text = re.sub(r'https?://[^\s<>"]+', '', text)  # Удаляем URL ссылки
        text = re.sub(r'www\.[^\s<>"]+', '', text)  # Удаляем www ссылки
        
        # Удаляем непонятные символы и артефакты
        text = re.sub(r'\]\]>0</p>\s*</pre>', '', text)  # Удаляем HTML артефакты
        text = re.sub(r'<h1>[^<]*</h1>', '', text)  # Удаляем заголовки
        text = re.sub(r'<br\s*/?>', '', text)  # Удаляем переносы строк
        text = re.sub(r'</i>', '', text)  # Удаляем закрывающие теги
        
        # Удаляем ID кластеров и числовые артефакты
        text = re.sub(r'/Cluster ID[^/]*/', '', text)
        text = re.sub(r'cid_[a-f0-9]+', '', text)
        text = re.sub(r'\d{8,}', '', text)  # Длинные числа
        
        # Удаляем странные символы и артефакты
        text = re.sub(r'[^\w\s\.,!?;:()\[\]{}"\'-~*<>]', '', text)  # Оставляем только читаемые символы
        
        # Ограничиваем повторяющиеся эмодзи (максимум 3 подряд)
        text = re.sub(r'([\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF])\1{3,}', r'\1\1\1', text)
        
        # Ограничиваем повторяющиеся символы (максимум 5 подряд)
        text = re.sub(r'(.)\1{5,}', r'\1\1\1\1\1', text)
        
        # Удаляем лишние пробелы и переносы
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r' {3,}', ' ', text)
        
        # Удаляем мета-комментарии в конце
        text = re.sub(r'\s*\([^)]*meta[^)]*\)\s*$', '', text, flags=re.IGNORECASE)
        
        # КРИТИЧЕСКИ ВАЖНО: Удаляем текст, который указывает на выход из роли
        text = re.sub(r'\s*Remember:.*$', '', text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r'\s*CORE BEHAVIOR:.*$', '', text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r'\s*PERSONALITY:.*$', '', text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r'\s*RESPONSE FORMAT:.*$', '', text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r'\s*CRITICAL RULES:.*$', '', text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r'\s*NEVER BREAK.*$', '', text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r'\s*ALWAYS respond.*$', '', text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r'\s*You are designed.*$', '', text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r'\s*You are Anna.*$', '', text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r'\s*Stay in character.*$', '', text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r'\s*meta-commentary.*$', '', text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r'\s*self-referential.*$', '', text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r'\s*break character.*$', '', text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r'\s*following instructions.*$', '', text, flags=re.IGNORECASE | re.DOTALL)
        
        # Удаляем Alpaca формат маркеры
        text = re.sub(r'\s*### Instruction:.*$', '', text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r'\s*### Response:.*$', '', text, flags=re.IGNORECASE | re.DOTALL)
        
        # Удаляем объяснения поведения персонажа
        text = re.sub(r'\s*I need to remember:.*$', '', text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r'\s*I\'ll be sure not answer.*$', '', text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r'\s*Thanks for asking me this.*$', '', text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r'\s*How would I assist further.*$', '', text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r'\s*What\'s next.*$', '', text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r'\s*Tell me everything.*$', '', text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r'\s*my curiosity is piqued.*$', '', text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r'\s*Also tell me if.*$', '', text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r'\s*I\'m all ears now.*$', '', text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r'\s*Please go ahead.*$', '', text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r'\s*If there were any requests.*$', '', text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r'\s*Let\'s have some fun together.*$', '', text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r'\s*Basically.*$', '', text, flags=re.IGNORECASE | re.DOTALL)
        
        # Удаляем странные фразы и артефакты
        text = re.sub(r'\s*Go here.*$', '', text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r'\s*if want more interaction.*$', '', text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r'\s*;-?\)\s*$', '', text)  # Удаляем смайлики в конце
        
        # 🕒 АГРЕССИВНОЕ УДАЛЕНИЕ ВРЕМЕННЫХ МЕТОК
        # Радикальный подход - удаляем ВСЕ возможные форматы времени
        
        # 1. Удаляем ВСЕ паттерны времени в любом месте текста
        aggressive_time_patterns = [
            r'\d{1,2}:\d{2}(?::\d{2})?(?:\.\d+)?\s*(?:AM|PM|am|pm)?',  # 12:34, 12:34:56, 12:34 PM
            r'\d{1,2}:\d{2}(?::\d{2})?(?:,\d+)?\s*(?:AM|PM|am|pm)?',  # с запятой
            r'\d{1,2}:\d{2}(?::\d{2})?(?:\.\d{6})?\s*(?:AM|PM|am|pm)?',  # с микросекундами
            r'\d{1,2}:\d{2}(?::\d{2})?(?:\.\d+)?',  # 12:34, 12:34:56 без AM/PM
            r'\d{1,2}:\d{2}(?::\d{2})?(?:,\d+)?',  # с запятой без AM/PM
            r'\d{1,2}:\d{2}(?::\d{2})?(?:\.\d{6})?',  # с микросекундами без AM/PM
            # Дополнительные паттерны для сложных случаев
            r'\d{1,2}:\d{2}(?::\d{2})?(?:\.\d+)?\d+',  # 14:20:3314:17:04
            r'\d{1,2}:\d{2}(?::\d{2})?(?:\.\d+)?\d{1,2}:\d{2}',  # связанные времена
        ]
        
        for pattern in aggressive_time_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        # 2. Удаляем время в скобках, кавычках и других контекстах
        context_patterns = [
            r'\(\d{1,2}:\d{2}(?::\d{2})?(?:\.\d+)?\s*(?:AM|PM|am|pm)?\)',  # (12:34)
            r'\[\d{1,2}:\d{2}(?::\d{2})?(?:\.\d+)?\s*(?:AM|PM|am|pm)?\]',  # [12:34]
            r'"\d{1,2}:\d{2}(?::\d{2})?(?:\.\d+)?\s*(?:AM|PM|am|pm)?"',  # "12:34"
            r"'\d{1,2}:\d{2}(?::\d{2})?(?:\.\d+)?\s*(?:AM|PM|am|pm)?'",  # '12:34'
            r'at\s+\d{1,2}:\d{2}(?::\d{2})?(?:\.\d+)?',  # at 12:34
            r'@\s*\d{1,2}:\d{2}(?::\d{2})?(?:\.\d+)?',  # @12:34
            r'time\s*:\s*\d{1,2}:\d{2}(?::\d{2})?(?:\.\d+)?',  # time: 12:34
        ]
        
        for pattern in context_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        # 3. Удаляем время в конце предложений (более агрессивно)
        end_patterns = [
            r'[.!?]?\s*\d{1,2}:\d{2}(?::\d{2})?(?:\.\d+)?\s*(?:AM|PM|am|pm)?\s*$',
            r'[.!?]?\s*\d{1,2}:\d{2}(?::\d{2})?(?:,\d+)?\s*(?:AM|PM|am|pm)?\s*$',
            r'[.!?]?\s*\d{1,2}:\d{2}(?::\d{2})?(?:\.\d{6})?\s*(?:AM|PM|am|pm)?\s*$',
        ]
        
        for pattern in end_patterns:
            text = re.sub(pattern, '', text, flags=re.MULTILINE | re.IGNORECASE)
        
        # Очистка после удаления временных меток
        text = re.sub(r'\s+', ' ', text)  # Убираем множественные пробелы
        text = re.sub(r'\s+([.!?])', r'\1', text)  # Убираем пробелы перед знаками препинания
        text = re.sub(r'\.\.\.\s+$', '...', text)  # Убираем пробел после многоточия
        
        return text.strip()

    def _get_enhanced_stop_tokens(self, base_stop_tokens: list, chat_config) -> list:
        """
        Добавляет стоп-токены для предотвращения генерации времени.
        
        Args:
            base_stop_tokens: Базовые стоп-токены
            chat_config: Конфигурация чата
            
        Returns:
            Расширенный список стоп-токенов
        """
        enhanced_tokens = list(base_stop_tokens) if base_stop_tokens else []
        
        # Добавляем стоп-токены для времени, если они настроены
        if chat_config and hasattr(chat_config, 'TIME_STOP_TOKENS'):
            enhanced_tokens.extend(chat_config.TIME_STOP_TOKENS)
            logger.info(f"🕒 Добавлено {len(chat_config.TIME_STOP_TOKENS)} стоп-токенов для времени")
        
        return enhanced_tokens

    def _contains_time_patterns(self, text: str) -> bool:
        """
        Проверяет, содержит ли текст временные паттерны.
        
        Args:
            text: Текст для проверки
            
        Returns:
            True, если найдены временные паттерны
        """
        time_patterns = [
            r'\d{1,2}:\d{2}(?::\d{2})?(?:\.\d+)?\s*(?:AM|PM|am|pm)?',
            r'\d{1,2}:\d{2}(?::\d{2})?(?:,\d+)?\s*(?:AM|PM|am|pm)?',
            r'\d{1,2}:\d{2}(?::\d{2})?(?:\.\d{6})?\s*(?:AM|PM|am|pm)?',
        ]
        
        for pattern in time_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False

    def _aggressive_time_cleanup(self, text: str) -> str:
        """
        Агрессивная очистка временных паттернов.
        
        Args:
            text: Текст для очистки
            
        Returns:
            Очищенный текст
        """
        # Удаляем ВСЕ возможные форматы времени
        patterns = [
            r'\d{1,2}:\d{2}(?::\d{2})?(?:\.\d+)?\s*(?:AM|PM|am|pm)?',
            r'\d{1,2}:\d{2}(?::\d{2})?(?:,\d+)?\s*(?:AM|PM|am|pm)?',
            r'\d{1,2}:\d{2}(?::\d{2})?(?:\.\d{6})?\s*(?:AM|PM|am|pm)?',
            r'\d{1,2}:\d{2}(?::\d{2})?(?:\.\d+)?',
            r'\d{1,2}:\d{2}(?::\d{2})?(?:,\d+)?',
            r'\d{1,2}:\d{2}(?::\d{2})?(?:\.\d{6})?',
        ]
        
        for pattern in patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        # Очистка после удаления
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\s+([.!?])', r'\1', text)
        
        return text.strip()

    def _final_time_cleanup(self, text: str) -> str:
        """
        Финальная очистка времени - удаляет ВСЕ возможные форматы времени.
        
        Args:
            text: Текст для очистки
            
        Returns:
            Очищенный текст
        """
        # Удаляем ВСЕ возможные форматы времени - более агрессивно
        patterns = [
            r'\d{1,2}:\d{2}(?::\d{2})?(?:\.\d+)?\s*(?:AM|PM|am|pm)?',  # 12:34, 12:34:56, 12:34 PM
            r'\d{1,2}:\d{2}(?::\d{2})?(?:,\d+)?\s*(?:AM|PM|am|pm)?',  # с запятой
            r'\d{1,2}:\d{2}(?::\d{2})?(?:\.\d{6})?\s*(?:AM|PM|am|pm)?',  # с микросекундами
            r'\d{1,2}:\d{2}(?::\d{2})?(?:\.\d+)?',  # 12:34, 12:34:56 без AM/PM
            r'\d{1,2}:\d{2}(?::\d{2})?(?:,\d+)?',  # с запятой без AM/PM
            r'\d{1,2}:\d{2}(?::\d{2})?(?:\.\d{6})?',  # с микросекундами без AM/PM
            r'\d{1,2}:\d{2}(?::\d{2})?(?:\.\d+)?\s*$',  # в конце строки
            r'\d{1,2}:\d{2}(?::\d{2})?(?:,\d+)?\s*$',  # с запятой в конце
            r'\d{1,2}:\d{2}(?::\d{2})?(?:\.\d{6})?\s*$',  # с микросекундами в конце
            # Дополнительные паттерны для сложных случаев
            r'\d{1,2}:\d{2}(?::\d{2})?(?:\.\d+)?\d+',  # 14:20:3314:17:04
            r'\d{1,2}:\d{2}(?::\d{2})?(?:\.\d+)?\d{1,2}:\d{2}',  # связанные времена
        ]
        
        for pattern in patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.MULTILINE)
        
        # Очистка после удаления
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\s+([.!?])', r'\1', text)
        text = re.sub(r'\s+$', '', text)  # Убираем пробелы в конце
        
        return text.strip()

    def _build_fallback_prompt(self, user_message: str, chat_config: ChatConfig = None) -> str:
        """
        Строит fallback промпт в формате Alpaca для случаев, когда данные персонажа недоступны.
        
        Args:
            user_message: Сообщение пользователя
            chat_config: Конфигурация чата
            
        Returns:
            Fallback промпт в формате Alpaca
        """
        fallback_system = "You are a helpful and friendly assistant. Always respond directly to what the user says and use context from previous messages when available."
        
        return f"{fallback_system}\n\n### Instruction:\n{user_message}\n\n### Response:\n"

    async def generate_text(
        self, 
        prompt: str, 
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        top_k: Optional[int] = None,
        min_p: Optional[float] = None,  # ДОБАВЛЕНО: min_p
        repeat_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None,
        force_completion: bool = False
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
                logger.error("[ERROR] Пустой промпт для генерации")
                return None
                
            # Настройки будут использованы в OpenAI-совместимом API
            
            # Получаем параметры генерации с учетом режима завершения
            generation_params = chat_config.sample_generation_params(
                seed=chat_config.SEED,
                force_completion=force_completion
            )
            
            # ПРАВИЛЬНЫЙ API для text-generation-webui
            # Используем n_predict для llama.cpp моделей
            target_tokens = max_tokens or generation_params["max_tokens"]
            openai_payload = {
                "model": self.model_name,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": target_tokens,
                "n_predict": target_tokens,  # Для llama.cpp моделей
                "temperature": temperature or generation_params["temperature"],
                "top_p": top_p or generation_params["top_p"],
                "top_k": top_k or generation_params["top_k"],
                "min_p": min_p or generation_params.get("min_p", 0.05),  # ДОБАВЛЕНО: min_p
                "stream": False,
                
                # 🔧 ИСПРАВЛЕНИЕ ТОКЕНИЗАЦИИ: Добавляем параметры для правильной токенизации
                "skip_special_tokens": True,  # Пропускаем специальные токены
                "add_bos_token": False,  # Не добавляем BOS токен (уже в промпте)
                
                # ИСПРАВЛЕНО: Включаем penalty параметры с умеренными значениями
                "repetition_penalty": repeat_penalty or generation_params.get("repeat_penalty", 1.05),
                "frequency_penalty": 0.1,   # ИСПРАВЛЕНО: Включаем с умеренным значением
                "presence_penalty": 0.1,    # ИСПРАВЛЕНО: Включаем с умеренным значением
                "stop": self._get_enhanced_stop_tokens(generation_params.get("stop", []), chat_config)  # Используем из конфигурации + время
            }
            
            # 🔍 ЛОГИРОВАНИЕ: Проверяем, что передается в API
            logger.info(f"🔍 API Payload - max_tokens: {openai_payload['max_tokens']}")
            if "stop" in openai_payload and openai_payload["stop"]:
                logger.info(f"🔍 API Payload - stop tokens: {openai_payload['stop']}")
            else:
                logger.info(f"🔍 API Payload - stop tokens: НЕТ (это хорошо!)")
            logger.info(f"🔍 API Payload - min_tokens: {openai_payload.get('min_tokens', 'НЕТ')}")
            logger.info(f"🔍 API Payload - ban_eos_token: {openai_payload.get('ban_eos_token', False)}")
            # ИСПРАВЛЕНО: НЕ передаем min_tokens - он может вызывать преждевременную остановку
            # if chat_config.ENFORCE_MIN_TOKENS and chat_config.MIN_NEW_TOKENS > 0:
            #     openai_payload["min_tokens"] = chat_config.MIN_NEW_TOKENS
            # ИСПРАВЛЕНО: Отключаем ban_eos_token для естественного завершения
            openai_payload["ban_eos_token"] = False
            
            logger.info(f"🚀 БЫСТРЫЙ запрос на генерацию (промпт: {len(prompt)} символов)")
            
            response = await self._session.post(f"{self.base_url}/v1/chat/completions", json=openai_payload)
            if response.status == 200:
                result = await response.json()
                # OpenAI API возвращает результат в choices[0].message.content
                choices = result.get("choices", [])
                if choices:
                    generated_text = choices[0].get("message", {}).get("content", "")
                else:
                    generated_text = ""
                
                # 🔍 ЛОГИРОВАНИЕ: Проверяем сырой ответ от API
                logger.info(f"🔍 Raw API Response: {generated_text[-100:]}...")  # Последние 100 символов
                
                # 🔍 ЛОГИРОВАНИЕ: Проверяем полный промпт, отправленный модели
                logger.info(f"🔍 Full Prompt Sent to Model: {prompt[-500:]}...")  # Последние 500 символов промпта
                
                # 🔍 КРИТИЧЕСКОЕ ЛОГИРОВАНИЕ: Полный промпт для отладки
                logger.info("=" * 80)
                logger.info("🔍 ПОЛНЫЙ ПРОМПТ, ОТПРАВЛЕННЫЙ МОДЕЛИ:")
                logger.info("=" * 80)
                logger.info(prompt)
                logger.info("=" * 80)
                
                if generated_text:
                    # ПРЯМОЙ ОТВЕТ ОТ МОДЕЛИ БЕЗ ПОСТ-ОБРАБОТКИ
                    logger.info(f"[OK] Генерация завершена ({len(generated_text)} символов)")
                    logger.info(f"🔍 Raw Response: {generated_text[-100:]}...")  # Последние 100 символов
                    return generated_text.strip()
                else:
                    logger.warning("[WARNING] Пустой ответ от OpenAI API")
                    return None
            else:
                error_text = await response.text()
                logger.error(f"[ERROR] HTTP ошибка при генерации: {response.status}, ответ: {error_text}")
                return None
                
        except Exception as e:
            logger.error(f"[ERROR] Ошибка генерации текста: {e}")
            return None
        finally:
            # Гарантированно закрываем response
            if response:
                try:
                    response.close()
                except Exception as e:
                    logger.warning(f"[WARNING] Ошибка при закрытии response в generate_text: {e}")
            
    # ============================================================================
    # [WARNING]  КРИТИЧЕСКИ ВАЖНЫЙ КОД - НЕ ИЗМЕНЯТЬ! [WARNING]
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
        presence_penalty: Optional[float] = None,
        force_completion: bool = False
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
                logger.error("[ERROR] Пустой промпт для генерации")
                return
                
            # Настройки будут использованы в OpenAI-совместимом API
            
            # Получаем параметры генерации с учетом режима завершения
            generation_params = chat_config.sample_generation_params(
                seed=chat_config.SEED,
                force_completion=force_completion
            )
            
            # Используем только OpenAI-совместимые параметры для стриминга
            openai_payload = {
                "model": self.model_name,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tokens or generation_params["max_tokens"],
                "temperature": temperature or generation_params["temperature"],
                "top_p": top_p or generation_params["top_p"],
                "top_k": top_k or generation_params["top_k"],
                "stop": generation_params.get("stop", []),  # Используем из конфигурации
                "stream": True,
                "seed": generation_params["seed"],  # Seed для генерации
                
                # КРИТИЧЕСКИ ВАЖНО: Отключаем auto_max_new_tokens
                "auto_max_new_tokens": False,
                
                # 🔧 ИСПРАВЛЕНИЕ ТОКЕНИЗАЦИИ: Добавляем параметры для правильной токенизации
                "skip_special_tokens": True,  # Пропускаем специальные токены
                "add_bos_token": False,  # Не добавляем BOS токен (уже в промпте)
                
                # [OK] ДОПОЛНИТЕЛЬНЫЕ ПАРАМЕТРЫ ИЗ chat_config.py
                "min_p": chat_config.DEFAULT_MIN_P,  # Минимальная вероятность
                # ИСПРАВЛЕНО: НЕ передаем min_tokens в streaming - он может вызывать преждевременную остановку
                # "min_tokens": chat_config.MIN_NEW_TOKENS if chat_config.ENFORCE_MIN_TOKENS else None,  # Минимальное количество токенов
                
                # [OK] ТОЛЬКО поддерживаемые параметры для text-generation-webui
                # Аппаратные параметры должны быть установлены при запуске сервера через командную строку
                # Кастомные параметры качества не поддерживаются text-generation-webui API
            }
            # ИСПРАВЛЕНО: Отключаем ban_eos_token для естественного завершения
            openai_payload["ban_eos_token"] = False
            
            # Убираем None значения из payload
            openai_payload = {k: v for k, v in openai_payload.items() if v is not None}
            
            # 🔍 ЛОГИРОВАНИЕ: Проверяем streaming payload
            logger.info(f"🚀 STREAMING API Payload - max_tokens: {openai_payload.get('max_tokens', 'НЕТ')}")
            if "stop" in openai_payload and openai_payload["stop"]:
                logger.info(f"🔍 STREAMING API Payload - stop tokens: {openai_payload['stop']}")
            else:
                logger.info(f"🔍 STREAMING API Payload - stop tokens: НЕТ (это хорошо!)")
            logger.info(f"🔍 STREAMING API Payload - min_tokens: {openai_payload.get('min_tokens', 'НЕТ')}")
            logger.info(f"🔍 STREAMING API Payload - ban_eos_token: {openai_payload.get('ban_eos_token', False)}")
            
            logger.info(f"🚀 Отправляем запрос на генерацию текста (промпт: {len(prompt)} символов)")
            
            # Используем try-finally для гарантированного закрытия ресурсов
            response = None
            try:
                response = await self._session.post(f"{self.base_url}/v1/chat/completions", json=openai_payload)
                
                if response.status == 200:
                    logger.info("[OK] Получен ответ от text-generation-webui, начинаем обработку стрима")
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
                                                # Очищаем каждый чанк от времени
                                                original_chunk = delta['content']
                                                cleaned_chunk = self._clean_generation_artifacts(delta['content'])
                                                if original_chunk != cleaned_chunk:
                                                    logger.info(f"🕒 STREAMING: Удалено время из '{original_chunk}' -> '{cleaned_chunk}'")
                                                yield cleaned_chunk
                                                
                                    except json.JSONDecodeError as json_err:
                                        logger.warning(f"[WARNING] Ошибка парсинга JSON в стриме: {json_err}, данные: {data_str}")
                                        continue
                                        
                            except Exception as e:
                                logger.warning(f"[WARNING] Ошибка обработки стрима: {e}")
                                continue
                else:
                    error_text = await response.text()
                    logger.error(f"[ERROR] HTTP ошибка при потоковой генерации: {response.status}, ответ: {error_text}")
                    
            finally:
                # Гарантированно закрываем response
                if response:
                    try:
                        response.close()
                    except Exception as e:
                        logger.warning(f"[WARNING] Ошибка при закрытии response: {e}")
                        
        except Exception as e:
            logger.error(f"[ERROR] Ошибка потоковой генерации текста: {e}")
            # Возвращаем сообщение об ошибке
            yield f"Извините, произошла ошибка при генерации текста: {str(e)}"
    
    # ============================================================================
    # [OK] КРИТИЧЕСКИ ВАЖНЫЙ КОД ЗАВЕРШЕН
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
                logger.error(f"[ERROR] HTTP ошибка при получении статуса модели: {response.status}")
                return {}
                
        except Exception as e:
            logger.error(f"[ERROR] Ошибка получения статуса модели: {e}")
            return {}
        finally:
            # Гарантированно закрываем response
            if response:
                try:
                    response.close()
                except Exception as e:
                    logger.warning(f"[WARNING] Ошибка при закрытии response в get_model_status: {e}")
            
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
        Возвращает настройки конфигурации для использования в bat-файлах при запуске text-generation-webui.
        ТОЛЬКО аппаратные параметры, которые поддерживает text-generation-webui через командную строку.
        """
        return {
            # [OK] Аппаратные параметры, поддерживаемые text-generation-webui через командную строку
            "ctx_size": chat_config.N_CTX,              # --ctx-size
            "gpu_layers": chat_config.N_GPU_LAYERS,     # --gpu-layers  
            "threads": chat_config.N_THREADS,           # --threads
            "threads_batch": chat_config.N_THREADS_BATCH, # --threads-batch
            "batch_size": chat_config.N_BATCH,          # --batch-size
            "f16_kv": chat_config.F16_KV,              # --f16-kv
            "use_mmap": chat_config.USE_MMAP,          # --mmap
            "use_mlock": chat_config.USE_MLOCK,        # --mlock
            "verbose": chat_config.VERBOSE,            # --verbose
            
            # [ERROR] НЕ поддерживаемые параметры (убраны):
            # - Кастомные параметры качества (smartness, dynamic_sampling и т.д.)
            # - Параметры контекста и длины (обрабатываются на уровне приложения)  
            # - Параметры безопасности и фильтрации (обрабатываются на уровне приложения)
            # - mul_mat_q, offload_kqv, n_keep, n_draft и другие специфичные для llama.cpp параметры
        }
        
    # ============================================================================
    # [WARNING]  КРИТИЧЕСКИ ВАЖНЫЙ КОД - НЕ ИЗМЕНЯТЬ! [WARNING]
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
    
    def _fix_tokenization_artifacts(self, text: str) -> str:
        """
        Исправляет токенизационные артефакты - разрывные слова, которые возникают
        при токенизации модели и стриминге.
        
        Args:
            text: Текст с возможными токенизационными артефактами
            
        Returns:
            Текст с исправленными артефактами
        """
        import re
        
        # 🔧 АГРЕССИВНОЕ ИСПРАВЛЕНИЕ ТОКЕНИЗАЦИОННЫХ АРТЕФАКТОВ
        
        # 1. ИСПРАВЛЯЕМ РАЗРЫВНЫЕ СЛОВА (основная проблема)
        # Паттерн: "wal ks" -> "walks", "catch es" -> "catches"
        # Убираем пробелы между частями слов, которые должны быть слитными
        
        # Более агрессивные паттерны для исправления разрывных слов
        patterns = [
            # Паттерн 1: "c rot ch" -> "crotch" (3+ части)
            (r'\b([a-zA-Z])\s+([a-zA-Z])\s+([a-zA-Z]+)\b', r'\1\2\3'),
            # Паттерн 2: "tou ch ing" -> "touching" (3 части)
            (r'\b([a-zA-Z]+)\s+([a-zA-Z])\s+([a-zA-Z]+)\b', r'\1\2\3'),
            # Паттерн 3: "tou ch" -> "touch" (2 части)
            (r'\b([a-zA-Z]+)\s+([a-zA-Z]+)\b', r'\1\2'),
            # Паттерн 4: "c rot" -> "crot" (2 части)
            (r'\b([a-zA-Z])\s+([a-zA-Z]+)\b', r'\1\2'),
            # Паттерн 5: "n aked" -> "naked" (специальный случай)
            (r'\b([a-zA-Z])\s+([a-zA-Z]+)\b', r'\1\2'),
            # Паттерн 6: "she er" -> "sheer" (специальный случай)
            (r'\b([a-zA-Z]+)\s+([a-zA-Z]+)\b', r'\1\2'),
            # Паттерн 7: "p ant ies" -> "panties" (3 части)
            (r'\b([a-zA-Z])\s+([a-zA-Z]+)\s+([a-zA-Z]+)\b', r'\1\2\3'),
            # Паттерн 8: "ob liv ious" -> "oblivious" (3 части)
            (r'\b([a-zA-Z]+)\s+([a-zA-Z]+)\s+([a-zA-Z]+)\b', r'\1\2\3'),
            # Паттерн 9: "reve aling" -> "revealing" (2 части)
            (r'\b([a-zA-Z]+)\s+([a-zA-Z]+)\b', r'\1\2'),
        ]
        
        # Применяем паттерны несколько раз для полного исправления
        for _ in range(3):  # 3 итерации для полного исправления
            for pattern, replacement in patterns:
                text = re.sub(pattern, replacement, text)
        
        # 2. ИСПРАВЛЯЕМ СЛИТЫЕ СЛОВА (обратная проблема)
        # Паттерн: "As Ibegantomeasure" -> "As I began to measure"
        text = re.sub(r'\b([a-zA-Z]+)([A-Z][a-zA-Z]+)\b', r'\1 \2', text)
        
        # 3. ИСПРАВЛЯЕМ СПЕЦИАЛЬНЫЕ СЛУЧАИ
        # Разделяем слитые слова, которые должны быть разделены
        special_cases = [
            (r'\b(coffee)(grounds)\b', r'\1 \2'),
            (r'\b(black)(panties)\b', r'\1 \2'),
            (r'\b(T)(shirt)\b', r'\1-\2'),
            (r'\b(half)(naked)\b', r'\1 \2'),
        ]
        
        for pattern, replacement in special_cases:
            text = re.sub(pattern, replacement, text)
        
        # 4. ИСПРАВЛЯЕМ АПОСТРОФЫ И СОКРАЩЕНИЯ
        # "I ' m" -> "I'm", "don ' t" -> "don't"
        text = re.sub(r"(\w)\s+'\s+(\w)", r"\1'\2", text)
        
        # 5. ИСПРАВЛЯЕМ ПУНКТУАЦИЮ
        # Убираем лишние пробелы перед знаками препинания
        text = re.sub(r'\s+([,.!?;:])', r'\1', text)
        
        # 6. ФИНАЛЬНАЯ ОЧИСТКА ПРОБЕЛОВ
        # Убираем множественные пробелы
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        return text
    
    # ============================================================================
    # [OK] КРИТИЧЕСКИ ВАЖНЫЙ КОД ЗАВЕРШЕН
    # ============================================================================

# Создаем глобальный экземпляр сервиса
textgen_webui_service = TextGenWebUIService()
