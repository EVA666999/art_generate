import sys
import copy
import json
import time
import traceback
import threading
import queue
from typing import Any, Dict
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

import httpx
import torch
from loguru import logger

from app.schemas.generation import GenerationSettings, GenerationResponse
from app.config.generation_defaults import DEFAULT_GENERATION_PARAMS
from app.config.default_prompts import (
    get_default_negative_prompts, 
    get_default_positive_prompts
)
from app.utils.generation_stats import generation_stats
from app.utils.image_saver import save_image
from app.config.paths import IMAGES_PATH
from app.config.cuda_config import optimize_memory, get_gpu_memory_info


# Добавляем корень проекта в путь для импорта
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def get_default_generation_params() -> Dict[str, Any]:
    """
    Получить дефолтные параметры генерации из конфига.
    
    Returns:
        Dict[str, Any]: Словарь с дефолтными параметрами
    """
    # Создаем глубокую копию, чтобы не изменять оригинал
    return copy.deepcopy(DEFAULT_GENERATION_PARAMS)

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
        start_time = time.time()
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
            request_params = get_default_generation_params()
            user_params = settings.dict()
            request_params.update(user_params)
            request_params["negative_prompt"] = negative_prompt
            
            # Обработка VAE настроек
            if settings.use_vae is not None:
                # Пользователь хочет контролировать VAE
                if settings.use_vae:
                    # Включить VAE
                    vae_model = settings.vae_model or VAE_SETTINGS["model"]
                    if "override_settings" not in request_params:
                        request_params["override_settings"] = {}
                    request_params["override_settings"]["sd_vae"] = vae_model
                    request_params["override_settings"]["sd_vae_overrides_per_model_preferences"] = True
                else:
                    # Отключить VAE
                    if "override_settings" not in request_params:
                        request_params["override_settings"] = {}
                    request_params["override_settings"]["sd_vae"] = None
                    request_params["override_settings"]["sd_vae_overrides_per_model_preferences"] = False
            

            
            if not request_params.get("scheduler") or request_params["scheduler"] == "Automatic":
                request_params["scheduler"] = "Karras"
            
            seed = request_params.get("seed", -1)
            n_samples = request_params.get("n_samples", "NOT_SET")
            self._log("INFO", f"Используемый seed: {seed}, n_samples: {n_samples}")
            
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
                
                # Используем результат как есть
                processed_result = result
                
                # Получаем информацию о сиде
                info = processed_result.get("info", "{}")
                try:
                    info_dict = json.loads(info)
                    actual_seed = info_dict.get("seed", -1)
                except Exception:
                    actual_seed = -1
                
                # Сохраняем изображения в отдельном потоке
                saved_paths = []
                images = processed_result.get("images", [])
                
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
                generation_response = GenerationResponse.from_api_response(processed_result)
                generation_response.saved_paths = saved_paths
                generation_response.seed = actual_seed
                
                # Обновляем статистику
                execution_time = time.time() - start_time
                await self.update_generation_stats(settings, generation_response, execution_time)
                
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

    async def update_generation_stats(self, settings: GenerationSettings, generation_response: GenerationResponse, execution_time: float):
        """Обновляет статистику генерации"""
        try:
            
            # Формируем параметры для статистики
            params = settings.dict()
            
            # Получаем информацию из результата
            info = generation_response.info
            if isinstance(info, str):
                try:
                    info_dict = json.loads(info)
                except:
                    info_dict = {}
            else:
                info_dict = info or {}
            
            # Обновляем параметры из результата
            # Используем реальные настройки, которые были отправлены, а не ответ API
            params.update({
                "sampler_name": settings.sampler_name or info_dict.get("sampler_name", "unknown"),
                "steps": settings.steps or int(info_dict.get("steps", 0)),
                "width": settings.width or int(info_dict.get("width", 0)),
                "height": settings.height or int(info_dict.get("height", 0)),
                "cfg_scale": settings.cfg_scale or float(info_dict.get("cfg_scale", 0)),
                "scheduler": settings.scheduler or info_dict.get("scheduler", "unknown"),
                "seed": generation_response.seed,
                "model": info_dict.get("model", "unknown"),
                "hr_scale": settings.hr_scale or float(info_dict.get("hr_scale", 0)),
                "denoising_strength": settings.denoising_strength or float(info_dict.get("denoising_strength", 0)),
                "clip_skip": settings.clip_skip or int(info_dict.get("clip_skip", 0)),
                "batch_size": settings.batch_size or int(info_dict.get("batch_size", 0)),
                "n_iter": settings.n_iter or int(info_dict.get("n_iter", 0)),
                "n_samples": 1,  # Принудительно один сэмпл
                "restore_faces": settings.restore_faces or bool(info_dict.get("restore_faces", False)),
                "hr_upscaler": settings.hr_upscaler or info_dict.get("hr_upscaler", "unknown")
            })
            
            # Логируем значения для отладки
            self._log("INFO", f"[STATS] Settings steps: {settings.steps}, API info steps: {info_dict.get('steps')}, Final steps: {params['steps']}")
            self._log("INFO", f"[STATS] Settings sampler: {settings.sampler_name}, API info sampler: {info_dict.get('sampler_name')}, Final sampler: {params['sampler_name']}")
            
            # Формируем результат для статистики
            result = {
                "seed": generation_response.seed,
                "info": generation_response.info,
                "width": generation_response.width,
                "height": generation_response.height,
                "sampler_name": info_dict.get("sampler_name", ""),
                "cfg_scale": info_dict.get("cfg_scale", 0),
                "steps": info_dict.get("steps", 0),
                "batch_size": info_dict.get("batch_size", 0),
                "restore_faces": info_dict.get("restore_faces", False),
                "face_restoration_model": info_dict.get("face_restoration_model", ""),
                "sd_model_hash": info_dict.get("sd_model_hash", ""),
                "denoising_strength": info_dict.get("denoising_strength", 0),
                "clip_skip": info_dict.get("clip_skip", 0)
            }
            
            # Формируем detailed информацию для статистики
            detailed_info = {
                "saved_paths": generation_response.saved_paths,
                "status": "success",
                "service": "GenerationService",
                "seed": generation_response.seed,
                "model": info_dict.get("model", "unknown")
            }
            
            # Добавляем в статистику
            generation_stats.add_generation(params, execution_time, result, detailed_info)
            self._log("INFO", f"Статистика генерации обновлена")
            
        except Exception as e:
            self._log("ERROR", f"Ошибка при обновлении статистики: {str(e)}")
            logger.error(f"Ошибка при обновлении статистики: {str(e)}") 