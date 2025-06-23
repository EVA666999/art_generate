"""
Сервис для улучшения лиц на сгенерированных изображениях
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
from app.config.generation_defaults import DEFAULT_GENERATION_PARAMS, ADETAILER_SETTINGS
from app.utils.generation_stats import generation_stats
from app.utils.memory_utils import get_memory_usage, unload_sd_memory
from app.utils.prompt_utils import get_default_positive_prompts, get_default_negative_prompts

logger = logging.getLogger(__name__)

class FaceRefinementService:
    """Сервис для улучшения лиц на изображениях"""
    
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

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True
    )
    async def _make_api_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Выполняет запрос к API с повторными попытками при таймауте"""
        try:
            # Логируем настройки ADetailer
            if "alwayson_scripts" in payload and "ADetailer" in payload["alwayson_scripts"]:
                logger.info(f"ADetailer settings in payload: {json.dumps(payload['alwayson_scripts']['ADetailer'], indent=2)}")
            else:
                logger.warning("ADetailer settings not found in payload!")
            
            logger.info(f"Full payload: {json.dumps(payload, indent=2)}")
            response = await self.client.post(
                f"{self.api_url}/sdapi/v1/txt2img",
                json=payload
            )
            response.raise_for_status()
            
            # Логируем ответ API
            response_data = response.json()
            logger.info(f"API response: {json.dumps(response_data, indent=2)}")
            
            # Проверяем наличие ADetailer в ответе
            if "info" in response_data:
                info = response_data["info"]
                if isinstance(info, str):
                    try:
                        info = json.loads(info)
                        if "alwayson_scripts" in info and "ADetailer" in info["alwayson_scripts"]:
                            logger.info(f"ADetailer found in API response: {json.dumps(info['alwayson_scripts']['ADetailer'], indent=2)}")
                    except:
                        pass
            
            return response_data
        except httpx.TimeoutException as e:
            logger.warning(f"Timeout occurred, retrying... Error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"API request failed: {str(e)}")
            raise
        
    async def generate_image(self, settings: GenerationSettings) -> GenerationResponse:
        """Генерация изображения с поддержкой Face Detailer"""
        start_time = time.time()
        logger.info("Starting image generation in FaceRefinementService")
        
        try:
            # Проверяем необходимость очистки памяти
            current_time = time.time()
            if current_time - self.last_cleanup > self.cleanup_interval:
                logger.info("Performing periodic memory cleanup")
                await unload_sd_memory(self.api_url)
                self.last_cleanup = current_time
            
            # Логируем использование памяти до генерации
            memory_before = get_memory_usage()
            logger.info(f"Memory usage before generation: {memory_before}")
            
            # Добавляем дефолтные промпты только если они включены в настройках
            if settings.use_default_prompts:
                logger.info("Adding default prompts")
                default_positive = get_default_positive_prompts()
                default_negative = get_default_negative_prompts()
                
                # Объединяем с пользовательскими промптами
                settings.prompt = f"{settings.prompt}, {default_positive}" if settings.prompt else default_positive
                settings.negative_prompt = f"{settings.negative_prompt}, {default_negative}" if settings.negative_prompt else default_negative
                logger.info(f"Final prompt: {settings.prompt}")
                logger.info(f"Final negative prompt: {settings.negative_prompt}")

            # Подготавливаем параметры запроса
            payload = self._prepare_payload(settings)
            logger.info("Payload prepared successfully")
            
            # Выполняем запрос к API с повторными попытками
            api_response = await self._make_api_request(payload)
            logger.info("Successfully received API response")
            
            # Проверяем наличие изображений в ответе
            if not api_response.get("images"):
                logger.error("No images in API response")
                logger.error(f"API response: {json.dumps(api_response, indent=2)}")
                raise ValueError("No images in API response")
            
            logger.info("Creating GenerationResponse from API response")
            result = GenerationResponse.from_api_response(api_response)
            logger.info("GenerationResponse created successfully")
            
            # Записываем статистику
            execution_time = time.time() - start_time
            logger.info(f"Stats prompt: {settings.prompt}")
            logger.info(f"Stats negative prompt: {settings.negative_prompt}")
            self._save_generation_stats(settings, api_response, execution_time)
            logger.info(f"Generation completed in {execution_time:.2f} seconds")

            # Очищаем память после генерации
            await unload_sd_memory(self.api_url)
            
            # Логируем использование памяти после генерации
            memory_after = get_memory_usage()
            logger.info(f"Memory usage after generation: {memory_after}")
            logger.info(f"Memory difference: {memory_after['rss'] - memory_before['rss']:.2f} MB")
            
            return result
            
        except Exception as e:
            logger.error(f"Error in generate_image: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise
        finally:
            # Очищаем память в любом случае
            await unload_sd_memory(self.api_url)

    def _prepare_payload(self, settings: GenerationSettings) -> Dict[str, Any]:
        """
        Подготовка параметров запроса
        """
        # Базовые параметры из дефолтных настроек
        payload = DEFAULT_GENERATION_PARAMS.copy()
        
        # Обновляем настройки из объекта settings
        settings_dict = settings.dict(exclude_none=True)
        payload.update(settings_dict)
        
        # Удаляем None значения
        payload = {k: v for k, v in payload.items() if v is not None}
        
        # Логируем финальный payload
        logger.info(f"Final payload with ADetailer: {json.dumps(payload, indent=2)}")
        
        return payload
        
    def _save_generation_stats(self, settings: GenerationSettings, result: Dict[str, Any], execution_time: float) -> None:
        """
        Сохранение статистики генерации
        Args:
            settings: Настройки генерации
            result: Результат генерации
            execution_time: Время выполнения
        """
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
            settings_dict["sampler_name"] = info.get("sampler_name", "unknown")
            settings_dict["steps"] = int(info.get("steps", 0))
            settings_dict["width"] = int(info.get("width", 0))
            settings_dict["height"] = int(info.get("height", 0))
            settings_dict["cfg_scale"] = float(info.get("cfg_scale", 0))
            settings_dict["denoising_strength"] = float(info.get("denoising_strength", 0))
            
            # Добавляем информацию о ADetailer из payload
            if "alwayson_scripts" in result and "ADetailer" in result["alwayson_scripts"]:
                adetailer_args = result["alwayson_scripts"]["ADetailer"].get("args", [])
                if len(adetailer_args) > 1 and isinstance(adetailer_args[1], dict):
                    settings_dict["adetailer"] = {
                        "enabled": adetailer_args[0],
                        "model": adetailer_args[1].get("ad_model", "unknown"),
                        "steps": adetailer_args[1].get("ad_steps", 0),
                        "cfg_scale": adetailer_args[1].get("ad_cfg_scale", 0),
                        "denoising_strength": adetailer_args[1].get("ad_denoising_strength", 0)
                    }
            else:
                # Если ADetailer не найден в результате, берем из настроек
                settings_dict["adetailer"] = {
                    "enabled": True,
                    "model": "face_yolov8n.pt",
                    "steps": 101,
                    "cfg_scale": 5,
                    "denoising_strength": 0.4
                }
            
            logger.info(f"Saving stats: {json.dumps(settings_dict, ensure_ascii=False, indent=2)}")
            generation_stats.add_generation(settings_dict, execution_time)
        except Exception as e:
            logger.error(f"Ошибка при сохранении статистики: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")

    async def close(self):
        """Закрывает клиент"""
        await self.client.aclose()

    async def process_face_refinement(self, settings: FaceRefinementSettings) -> GenerationResponse:
        """
        Обработка улучшения лица
        
        Args:
            settings: Настройки улучшения лица
            
        Returns:
            GenerationResponse: Результат улучшения лица
        """
        try:
            logger.info(f"Starting face refinement with settings: {settings.dict()}")
            
            # Создаем настройки генерации из настроек улучшения лица
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
            
            # Генерируем изображение с улучшенным лицом
            result = await self.generate_image(generation_settings)
            
            logger.info("Face refinement completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Error in process_face_refinement: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise 