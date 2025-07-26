"""
Исправленный сервис для улучшения лиц на сгенерированных изображениях
Устранена проблема дублирования изображений
"""
import httpx
import json
import base64
from io import BytesIO
from PIL import Image
import time
from datetime import datetime
import traceback
from typing import Dict, Any, Optional
import logging
import os
from tenacity import retry, stop_after_attempt, wait_exponential

from app.schemas.generation import GenerationSettings, GenerationResponse, FaceRefinementSettings
import sys
from pathlib import Path

# Добавляем корень проекта в путь для импорта
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app.config.generation_defaults import DEFAULT_GENERATION_PARAMS
from app.config.default_prompts import get_default_positive_prompts, get_default_negative_prompts
from app.utils.generation_stats import generation_stats
from app.utils.memory_utils import get_memory_usage, unload_sd_memory, clear_gpu_memory, fix_device_conflict

logger = logging.getLogger(__name__)


class FaceRefinementService:
    """Исправленный сервис для улучшения лиц на изображениях"""
    
    def __init__(self, api_url: str):
        """
        :param api_url: URL Stable Diffusion WebUI API
        """
        self.api_url = api_url
        self.output_dir = "outputs/generated"
        os.makedirs(self.output_dir, exist_ok=True)
        # Увеличиваем таймаут до 5 минут
        self.client = httpx.AsyncClient(timeout=300.0)
        self.last_cleanup = time.time()
        self.cleanup_interval = 300  # 5 минут
        
        # НОВОЕ: Добавляем счетчик запросов для отладки
        self._request_counter = 0

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True
    )
    async def _make_api_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """ИСПРАВЛЕННЫЙ: Выполняет запрос к API с детальным логированием"""
        
        # НОВОЕ: Увеличиваем счетчик запросов
        self._request_counter += 1
        request_id = self._request_counter
        
        logger.info(f"[REQUEST-{request_id}] =========================")
        logger.info(f"[REQUEST-{request_id}] Начинаем API запрос")
        
        try:
            # ИСПРАВЛЕНО: Проверяем критические параметры ПЕРЕД отправкой
            logger.info(f"[REQUEST-{request_id}] КРИТИЧЕСКИЕ ПАРАМЕТРЫ:")
            logger.info(f"[REQUEST-{request_id}] - n_samples: {payload.get('n_samples', 'НЕ УСТАНОВЛЕН')}")
            logger.info(f"[REQUEST-{request_id}] - batch_size: {payload.get('batch_size', 'НЕ УСТАНОВЛЕН')}")
            logger.info(f"[REQUEST-{request_id}] - n_iter: {payload.get('n_iter', 'НЕ УСТАНОВЛЕН')}")
            logger.info(f"[REQUEST-{request_id}] - steps: {payload.get('steps', 'НЕ УСТАНОВЛЕН')}")
            logger.info(f"[REQUEST-{request_id}] - sampler_name: {payload.get('sampler_name', 'НЕ УСТАНОВЛЕН')}")
            
            # ИСПРАВЛЕНО: Принудительно устанавливаем правильные значения
            payload["n_samples"] = 1  # ПРИНУДИТЕЛЬНО ТОЛЬКО ОДНО ИЗОБРАЖЕНИЕ
            payload["batch_size"] = 1  # ПРИНУДИТЕЛЬНО ОДИН БАТЧ
            payload["n_iter"] = 1      # ПРИНУДИТЕЛЬНО ОДНА ИТЕРАЦИЯ
            
            logger.info(f"[REQUEST-{request_id}] ПОСЛЕ ПРИНУДИТЕЛЬНОЙ УСТАНОВКИ:")
            logger.info(f"[REQUEST-{request_id}] - n_samples: {payload['n_samples']}")
            logger.info(f"[REQUEST-{request_id}] - batch_size: {payload['batch_size']}")
            logger.info(f"[REQUEST-{request_id}] - n_iter: {payload['n_iter']}")
            
            # НОВОЕ: Детальное логирование ADetailer
            if "alwayson_scripts" in payload and "ADetailer" in payload["alwayson_scripts"]:
                adetailer_config = payload["alwayson_scripts"]["ADetailer"]
                logger.info(f"[REQUEST-{request_id}] ADETAILER КОНФИГУРАЦИЯ:")
                logger.info(f"[REQUEST-{request_id}] - Включен: {adetailer_config.get('args', [False])[0] if adetailer_config.get('args') else 'НЕТ ARGS'}")
                if len(adetailer_config.get('args', [])) > 1:
                    adetailer_settings = adetailer_config['args'][1]
                    logger.info(f"[REQUEST-{request_id}] - Модель: {adetailer_settings.get('ad_model', 'НЕ УСТАНОВЛЕНА')}")
                    logger.info(f"[REQUEST-{request_id}] - Шаги: {adetailer_settings.get('ad_steps', 'НЕ УСТАНОВЛЕНЫ')}")
                    logger.info(f"[REQUEST-{request_id}] - CFG: {adetailer_settings.get('ad_cfg_scale', 'НЕ УСТАНОВЛЕН')}")
            
            # ИСПРАВЛЕНО: Удаляем потенциально проблемные параметры
            problematic_params = ['images', 'init_images', 'mask']
            for param in problematic_params:
                if param in payload:
                    logger.warning(f"[REQUEST-{request_id}] Удаляем проблемный параметр: {param}")
                    del payload[param]
            
            # Отправляем запрос
            logger.info(f"[REQUEST-{request_id}] Отправляем HTTP запрос к {self.api_url}/sdapi/v1/txt2img")
            response = await self.client.post(
                f"{self.api_url}/sdapi/v1/txt2img",
                json=payload
            )
            response.raise_for_status()
            
            # Получаем ответ API
            response_data = response.json()
            
            # НОВОЕ: Детальный анализ ответа
            images_count = len(response_data.get('images', []))
            logger.info(f"[REQUEST-{request_id}] ОТВЕТ API:")
            logger.info(f"[REQUEST-{request_id}] - Получено изображений: {images_count}")
            logger.info(f"[REQUEST-{request_id}] - Ожидалось изображений: 1")
            
            if images_count != 1:
                logger.error(f"[REQUEST-{request_id}] ❌ ПРОБЛЕМА: Получено {images_count} изображений вместо 1!")
                # Логируем info для анализа
                info = response_data.get('info', '{}')
                logger.error(f"[REQUEST-{request_id}] Info из ответа: {info}")
            else:
                logger.info(f"[REQUEST-{request_id}] ✅ Получено корректное количество изображений")
            
            logger.info(f"[REQUEST-{request_id}] =========================")
            return response_data
            
        except httpx.TimeoutException as e:
            logger.warning(f"[REQUEST-{request_id}] Timeout occurred, retrying... Error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"[REQUEST-{request_id}] API request failed: {str(e)}")
            raise

    def _prepare_payload(self, settings: GenerationSettings) -> Dict[str, Any]:
        """
        ИСПРАВЛЕННАЯ: Подготовка параметров запроса с предотвращением дублирования
        """
        logger.info("=== ИСПРАВЛЕННАЯ ПОДГОТОВКА PAYLOAD ===")
        
        # ИСПРАВЛЕНО: Создаем чистую копию базовых настроек
        payload = {}
        
        # Добавляем ВСЕ параметры из DEFAULT_GENERATION_PARAMS
        essential_params = [
            'sampler_name', 'scheduler', 'steps', 'width', 'height', 'cfg_scale',
            'restore_faces', 'enable_hr', 'denoising_strength', 'hr_scale', 
            'hr_upscaler', 'hr_second_pass_steps', 'override_settings',
            'override_settings_restore_afterwards', 'send_images', 'save_images',
            'clip_skip', 'seed', 'eta_noise_seed_delta', 'alwayson_scripts', 
            'lora_models', 'script_args', 'hr_prompt', 'hr_negative_prompt'
        ]
        
        for param in essential_params:
            if param in DEFAULT_GENERATION_PARAMS:
                payload[param] = DEFAULT_GENERATION_PARAMS[param]
        
        logger.info(f"Базовые параметры добавлены: {list(payload.keys())}")
        
        # Детальное логирование важных параметров
        logger.info("=== ДЕТАЛЬНАЯ ПРОВЕРКА НАСТРОЕК ===")
        logger.info(f"Steps: {payload.get('steps', 'НЕ УСТАНОВЛЕН')}")
        logger.info(f"CFG Scale: {payload.get('cfg_scale', 'НЕ УСТАНОВЛЕН')}")
        logger.info(f"Sampler: {payload.get('sampler_name', 'НЕ УСТАНОВЛЕН')}")
        logger.info(f"Hires.fix включен: {'Да' if payload.get('enable_hr', False) else 'Нет'}")
        if payload.get('enable_hr', False):
            logger.info(f"Hires.fix scale: {payload.get('hr_scale', 'НЕ УСТАНОВЛЕН')}")
            logger.info(f"Hires.fix upscaler: {payload.get('hr_upscaler', 'НЕ УСТАНОВЛЕН')}")
            logger.info(f"Hires.fix steps: {payload.get('hr_second_pass_steps', 'НЕ УСТАНОВЛЕН')}")
        logger.info(f"ENSD: {payload.get('eta_noise_seed_delta', 'НЕ УСТАНОВЛЕН')}")
        logger.info(f"Denoising strength: {payload.get('denoising_strength', 'НЕ УСТАНОВЛЕН')}")
        logger.info(f"VAE: {'Отключен' if payload.get('override_settings', {}).get('sd_vae') is None else 'Включен'}")
        logger.info(f"ADetailer включен: {'Да' if 'alwayson_scripts' in payload and 'ADetailer' in payload['alwayson_scripts'] else 'Нет'}")
        logger.info(f"LoRA модели: {'Да' if 'lora_models' in payload else 'Нет'}")
        if 'lora_models' in payload:
            logger.info("=== ДЕТАЛЬНАЯ ИНФОРМАЦИЯ LoRA ===")
            for lora_name, lora_config in payload['lora_models'].items():
                logger.info(f"LoRA: {lora_name}")
                logger.info(f"  - name: {lora_config.get('name', 'НЕ УСТАНОВЛЕН')}")
                logger.info(f"  - weight: {lora_config.get('weight', 'НЕ УСТАНОВЛЕН')}")
                logger.info(f"  - enabled: {lora_config.get('enabled', 'НЕ УСТАНОВЛЕН')}")
                logger.info(f"  - path: {lora_config.get('path', 'НЕ УСТАНОВЛЕН')}")
            logger.info("=================================")
        if 'alwayson_scripts' in payload and 'ADetailer' in payload['alwayson_scripts']:
            adetailer_args = payload['alwayson_scripts']['ADetailer']['args']
            if len(adetailer_args) > 0 and isinstance(adetailer_args[0], dict):
                adetailer_config = adetailer_args[0]
                logger.info("=== ДЕТАЛЬНАЯ ИНФОРМАЦИЯ ADETAILER ===")
                logger.info(f"ADetailer model: {adetailer_config.get('ad_model', 'НЕ УСТАНОВЛЕН')}")
                logger.info(f"ADetailer prompt: {adetailer_config.get('ad_prompt', 'НЕ УСТАНОВЛЕН')}")
                logger.info(f"ADetailer negative prompt: {adetailer_config.get('ad_negative_prompt', 'НЕ УСТАНОВЛЕН')}")
                logger.info(f"ADetailer steps: {adetailer_config.get('ad_steps', 'НЕ УСТАНОВЛЕН')}")
                logger.info(f"ADetailer CFG: {adetailer_config.get('ad_cfg_scale', 'НЕ УСТАНОВЛЕН')}")
                logger.info(f"ADetailer sampler: {adetailer_config.get('ad_sampler_name', 'НЕ УСТАНОВЛЕН')}")
                logger.info(f"ADetailer denoising: {adetailer_config.get('ad_denoising_strength', 'НЕ УСТАНОВЛЕН')}")
                logger.info(f"ADetailer confidence: {adetailer_config.get('ad_confidence', 'НЕ УСТАНОВЛЕН')}")
                logger.info(f"ADetailer use_steps: {adetailer_config.get('ad_use_steps', 'НЕ УСТАНОВЛЕН')}")
                logger.info(f"ADetailer use_cfg_scale: {adetailer_config.get('ad_use_cfg_scale', 'НЕ УСТАНОВЛЕН')}")
                logger.info(f"ADetailer use_sampler: {adetailer_config.get('ad_use_sampler', 'НЕ УСТАНОВЛЕН')}")
                logger.info("==========================================")
            else:
                logger.info("ADetailer: неправильная структура args")
        logger.info("=====================================")
        
        # КРИТИЧЕСКИ ВАЖНО: Устанавливаем параметры для одного изображения
        payload.update({
            "n_samples": 1,     # ТОЛЬКО ОДНО ИЗОБРАЖЕНИЕ
            "batch_size": 1,    # ТОЛЬКО ОДИН БАТЧ  
            "n_iter": 1,        # ТОЛЬКО ОДНА ИТЕРАЦИЯ
            "save_grid": False, # НЕ СОХРАНЯТЬ СЕТКУ
        })
        
        logger.info("КРИТИЧЕСКИЕ параметры установлены:")
        logger.info(f"  n_samples: {payload['n_samples']}")
        logger.info(f"  batch_size: {payload['batch_size']}")
        logger.info(f"  n_iter: {payload['n_iter']}")
        logger.info(f"  save_grid: {payload['save_grid']}")
        
        # Обновляем пользовательскими настройками (НО НЕ КРИТИЧЕСКИМИ)
        settings_dict = settings.dict(exclude_none=True)
        safe_settings = {k: v for k, v in settings_dict.items() 
                        if k not in ['n_samples', 'batch_size', 'n_iter', 'save_grid']}
        payload.update(safe_settings)
        
        logger.info(f"Пользовательские настройки добавлены: {list(safe_settings.keys())}")
        
        # ADetailer уже включен через essential_params
        logger.info("ADetailer и LoRA модели включены через essential_params")
        
        # НОВОЕ: Финальная проверка критических параметров
        critical_check = {
            "n_samples": payload.get("n_samples"),
            "batch_size": payload.get("batch_size"), 
            "n_iter": payload.get("n_iter"),
            "save_grid": payload.get("save_grid")
        }
        logger.info(f"ФИНАЛЬНАЯ ПРОВЕРКА критических параметров: {critical_check}")
        
        # Проверяем на правильность
        if payload.get("n_samples") != 1:
            logger.error(f"❌ ОШИБКА: n_samples = {payload.get('n_samples')}, должно быть 1!")
            payload["n_samples"] = 1
            
        if payload.get("batch_size") != 1:
            logger.error(f"❌ ОШИБКА: batch_size = {payload.get('batch_size')}, должно быть 1!")
            payload["batch_size"] = 1
            
        if payload.get("n_iter") != 1:
            logger.error(f"❌ ОШИБКА: n_iter = {payload.get('n_iter')}, должно быть 1!")
            payload["n_iter"] = 1
        
        logger.info("ФИНАЛЬНЫЙ PAYLOAD готов")
        logger.info("=====================================")
        
        return payload

    async def generate_image(self, settings: GenerationSettings) -> GenerationResponse:
        """ИСПРАВЛЕННАЯ: Генерация изображения с предотвращением дублирования"""
        start_time = time.time()
        logger.info("🎯 НАЧИНАЕМ ГЕНЕРАЦИЮ ИЗОБРАЖЕНИЯ (ИСПРАВЛЕННАЯ ВЕРСИЯ)")
        
        try:
            # Добавляем дефолтные промпты если нужно
            if settings.use_default_prompts:
                logger.info("Добавляем дефолтные промпты")
                default_positive = get_default_positive_prompts()
                default_negative = get_default_negative_prompts()
                
                settings.prompt = f"{settings.prompt}, {default_positive}" if settings.prompt else default_positive
                settings.negative_prompt = f"{settings.negative_prompt}, {default_negative}" if settings.negative_prompt else default_negative

            # ИСПРАВЛЕНО: Подготавливаем payload с проверками
            payload = self._prepare_payload(settings)
            logger.info("✅ Payload подготовлен")
            
            # НОВОЕ: Дополнительная проверка перед отправкой
            if payload.get("n_samples") != 1:
                logger.error(f"❌ КРИТИЧЕСКАЯ ОШИБКА: n_samples = {payload.get('n_samples')}")
                raise ValueError(f"Неправильное значение n_samples: {payload.get('n_samples')}")
            
            # Выполняем запрос к API
            api_response = await self._make_api_request(payload)
            logger.info("✅ API запрос выполнен")
            
            # НОВОЕ: Проверяем количество изображений в ответе
            received_images = len(api_response.get("images", []))
            if received_images != 1:
                logger.error(f"❌ ПОЛУЧЕНО {received_images} ИЗОБРАЖЕНИЙ ВМЕСТО 1!")
                logger.error(f"Info: {api_response.get('info', 'НЕТ INFO')}")
                
                # ИСПРАВЛЕНИЕ: Если получили больше одного изображения, берем только первое
                if received_images > 1:
                    logger.warning("🔧 ИСПРАВЛЯЕМ: Берем только первое изображение")
                    api_response["images"] = [api_response["images"][0]]
                    logger.info("✅ Оставлено только одно изображение")
            
            # Создаем ответ
            result = GenerationResponse.from_api_response(api_response)
            logger.info("✅ GenerationResponse создан")
            
            # Записываем статистику
            execution_time = time.time() - start_time
            self._save_generation_stats(settings, api_response, execution_time)
            logger.info(f"✅ Генерация завершена за {execution_time:.2f} секунд")

            # Очищаем память
            await unload_sd_memory(self.api_url)
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Ошибка в generate_image: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise
        finally:
            # Очищаем память в любом случае
            await unload_sd_memory(self.api_url)

    def _save_generation_stats(self, settings: GenerationSettings, result: Dict[str, Any], execution_time: float) -> None:
        """Сохранение статистики генерации (без изменений)"""
        try:
            settings_dict = settings.dict()
            
            # Получаем информацию из результата
            info = result.get("info", {})
            if isinstance(info, str):
                try:
                    import json
                    info = json.loads(info)
                except:
                    info = {}
            
            # Обеспечиваем наличие ключей для статистики
            settings_dict["sampler_name"] = settings.sampler_name or info.get("sampler_name", "unknown")
            settings_dict["steps"] = settings.steps or int(info.get("steps", 0))
            settings_dict["width"] = settings.width or int(info.get("width", 0))
            settings_dict["height"] = settings.height or int(info.get("height", 0))
            settings_dict["cfg_scale"] = settings.cfg_scale or float(info.get("cfg_scale", 0))
            settings_dict["denoising_strength"] = settings.denoising_strength or float(info.get("denoising_strength", 0))
            
            # Добавляем информацию о количестве изображений
            settings_dict["images_generated"] = len(result.get("images", []))
            settings_dict["expected_images"] = 1
            
            logger.info(f"Сохраняем статистику: изображений получено {settings_dict['images_generated']}")
            
            detailed_info = {
                "saved_paths": [],
                "status": "success",
                "service": "FaceRefinementService",
                "images_count": settings_dict["images_generated"],
                "request_id": getattr(self, '_request_counter', 0)
            }
            
            generation_stats.add_generation(settings_dict, execution_time, result, detailed_info)
        except Exception as e:
            logger.error(f"Ошибка при сохранении статистики: {str(e)}")

    # Остальные методы без изменений...
    async def close(self):
        """Закрывает клиент"""
        await self.client.aclose()

    async def process_face_refinement(self, settings: FaceRefinementSettings) -> GenerationResponse:
        """Обработка улучшения лица (без изменений)"""
        try:
            logger.info(f"Starting face refinement with settings: {settings.dict()}")
            
            generation_settings = GenerationSettings(
                prompt=settings.prompt,
                negative_prompt=settings.negative_prompt,
                use_default_prompts=True,
                steps=settings.override_params.get("sampling_steps", DEFAULT_GENERATION_PARAMS["steps"]),
                cfg_scale=settings.override_params.get("cfg_scale", DEFAULT_GENERATION_PARAMS["cfg_scale"]),
                width=settings.override_params.get("width", DEFAULT_GENERATION_PARAMS["width"]),
                height=settings.override_params.get("height", DEFAULT_GENERATION_PARAMS["height"]),
                restore_faces=True,
                enable_hr=settings.override_params.get("enable_hr", DEFAULT_GENERATION_PARAMS["enable_hr"]),
                denoising_strength=settings.refinement_strength,
                hr_scale=settings.override_params.get("hr_scale", DEFAULT_GENERATION_PARAMS["hr_scale"]),
                hr_upscaler=settings.override_params.get("hr_upscaler", DEFAULT_GENERATION_PARAMS["hr_upscaler"]),
                hr_second_pass_steps=settings.override_params.get("hr_second_pass_steps", DEFAULT_GENERATION_PARAMS["hr_second_pass_steps"])
            )
            
            result = await self.generate_image(generation_settings)
            
            logger.info("Face refinement completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Error in process_face_refinement: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise 