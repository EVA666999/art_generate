from typing import Any, Dict, List
from app.schemas.generation import GenerationSettings, GenerationResponse
from app.config.generation_defaults import DEFAULT_GENERATION_PARAMS
import httpx
import json
import base64
from PIL import Image
from io import BytesIO
import time
from datetime import datetime
from app.utils.generation_stats import generation_stats
from loguru import logger
import os
from pathlib import Path
from app.utils.image_saver import save_image
from app.config.paths import IMAGES_PATH
import traceback
import torch
import threading
import queue
from concurrent.futures import ThreadPoolExecutor
from app.config.cuda_config import optimize_memory, get_gpu_memory_info

class GenerationService:
    """
    Сервис для взаимодействия с Stable Diffusion WebUI через API.
    Используется для генерации изображений по заданным параметрам.
    """
    def __init__(self, api_url: str) -> None:
        """
        :param api_url: URL Stable Diffusion WebUI API
        """
        self.api_url = api_url
        self.client = httpx.AsyncClient(timeout=60.0)
        self.output_dir = IMAGES_PATH
        self.output_dir.mkdir(exist_ok=True)
        
        # Создаем очередь для логов
        self.log_queue = queue.Queue()
        self.log_thread = threading.Thread(target=self._process_logs, daemon=True)
        self.log_thread.start()
        
        # Создаем пул потоков для сохранения изображений
        self.save_executor = ThreadPoolExecutor(max_workers=2)
        
        # Кэш для хранения последних результатов
        self._result_cache = {}
        self._cache_size = 10  # Максимальное количество кэшированных результатов

    def _process_logs(self):
        """Обработка логов в отдельном потоке"""
        while True:
            try:
                log_entry = self.log_queue.get()
                if log_entry is None:
                    break
                level, message = log_entry
                logger.log(level, message)
            except Exception as e:
                logger.error(f"Ошибка в потоке логирования: {str(e)}")

    def _log(self, level: str, message: str):
        """Добавляет сообщение в очередь логов"""
        self.log_queue.put((level, message))

    def _update_cache(self, key: str, value: Any):
        """Обновляет кэш результатов"""
        if len(self._result_cache) >= self._cache_size:
            # Удаляем самый старый элемент
            self._result_cache.pop(next(iter(self._result_cache)))
        self._result_cache[key] = value

    async def generate(self, settings: GenerationSettings) -> GenerationResponse:
        """Генерация изображения с заданными параметрами"""
        try:
            # Проверяем кэш
            cache_key = f"{settings.dict()}"
            if cache_key in self._result_cache:
                self._log("INFO", "Используем кэшированный результат")
                return self._result_cache[cache_key]

            # Оптимизируем память перед генерацией
            optimize_memory()
            
            # Получаем информацию о памяти GPU
            memory_info = get_gpu_memory_info()
            if memory_info:
                self._log("INFO", f"GPU Memory before generation: {memory_info}")
            
            # Получаем негативный промпт
            negative_prompt = settings.get_negative_prompt()
            
            # Формируем параметры запроса
            request_params = DEFAULT_GENERATION_PARAMS.copy()
            user_params = settings.dict()
            request_params.update(user_params)
            request_params["negative_prompt"] = negative_prompt
            
            if not request_params.get("scheduler") or request_params["scheduler"] == "Automatic":
                request_params["scheduler"] = "Karras"
            
            seed = request_params.get("seed", -1)
            self._log("INFO", f"Используемый seed: {seed}")
            
            # Отправляем запрос к API
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.api_url}/sdapi/v1/txt2img",
                    json=request_params,
                    timeout=300.0
                )
                response.raise_for_status()
                result = response.json()
                
                # Синхронизируем CUDA перед сохранением
                if torch.cuda.is_available():
                    torch.cuda.synchronize()
                
                # Получаем информацию о сиде
                info = result.get("info", "{}")
                try:
                    info_dict = json.loads(info)
                    actual_seed = info_dict.get("seed", -1)
                except:
                    actual_seed = -1
                
                # Сохраняем изображения в отдельном потоке
                saved_paths = []
                images = result.get("images", [])
                
                def save_image_task(image_data, index):
                    try:
                        prefix = f"gen_{actual_seed}_{index}"
                        saved_path = save_image(image_data, prefix=prefix)
                        return saved_path
                    except Exception as e:
                        self._log("ERROR", f"Ошибка при сохранении изображения {index}: {str(e)}")
                        return None
                
                # Запускаем сохранение в пуле потоков
                futures = []
                for i, image_base64 in enumerate(images):
                    if image_base64:
                        future = self.save_executor.submit(save_image_task, image_base64, i)
                        futures.append(future)
                
                # Собираем результаты
                for future in futures:
                    path = future.result()
                    if path:
                        saved_paths.append(path)
                
                # Создаем ответ
                generation_response = GenerationResponse.from_api_response(result)
                generation_response.saved_paths = saved_paths
                generation_response.seed = actual_seed
                
                # Обновляем статистику
                await self.update_generation_stats(settings, generation_response)
                
                # Кэшируем результат
                self._update_cache(cache_key, generation_response)
                
                # Оптимизируем память после генерации
                optimize_memory()
                
                # Получаем информацию о памяти GPU после генерации
                memory_info = get_gpu_memory_info()
                if memory_info:
                    self._log("INFO", f"GPU Memory after generation: {memory_info}")
                
                return generation_response
                
        except Exception as e:
            self._log("ERROR", f"Ошибка при генерации: {str(e)}")
            self._log("ERROR", f"Traceback: {traceback.format_exc()}")
            raise

    async def update_generation_stats(self, settings: GenerationSettings, generation_response: GenerationResponse):
        # Implementation of update_generation_stats method
        pass 