"""
Подробный тест генерации изображений с логированием
"""
import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path

import httpx


# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_generation.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


async def test_generation_with_logging():
    """Тест генерации изображений с подробным логированием"""
    
    # URL для тестирования
    base_url = "http://localhost:8000"
    generation_url = f"{base_url}/api/generation/generate"
    
    logger.info("=" * 80)
    logger.info("НАЧАЛО ТЕСТА ГЕНЕРАЦИИ ИЗОБРАЖЕНИЙ")
    logger.info("=" * 80)
    
    # Тестовые данные
    test_data = {
        "prompt": "beautiful woman, portrait, high quality, detailed face",
        "negative_prompt": "blurry, low quality, distorted",
        "width": 512,
        "height": 512,
        "steps": 20,
        "cfg_scale": 7.0,
        "seed": -1,
        "sampler_name": "DPM++ 2M Karras",
        "model_name": "v1-5-pruned.ckpt",
        "enable_adetailer": True,
        "adetailer_settings": {
            "ad_model": "face_yolov8n.pt",
            "ad_prompt": "face, portrait, beautiful, detailed",
            "ad_negative_prompt": "blurry, low quality, distorted",
            "ad_confidence": 0.3,
            "ad_dilate_erode": 4,
            "ad_x_offset": 0,
            "ad_y_offset": 0,
            "ad_mask_merge_invert": "None",
            "ad_mask_blur": 4,
            "ad_denoising_strength": 0.4,
            "ad_inpaint_only_masked": True,
            "ad_inpaint_only_masked_padding": 32,
            "ad_use_inpaint_width_height": False,
            "ad_inpaint_width": 512,
            "ad_inpaint_height": 512,
            "ad_use_steps": True,
            "ad_steps": 28,
            "ad_use_cfg_scale": True,
            "ad_cfg_scale": 7.0,
            "ad_use_sampler": True,
            "ad_sampler_name": "DPM++ 2M Karras",
            "ad_use_noise_multiplier": True,
            "ad_noise_multiplier": 1.0,
            "ad_use_clip_skip": True,
            "ad_clip_skip": 1,
            "ad_restore_face": False,
            "ad_controlnet_model": "None",
            "ad_controlnet_module": "None",
            "ad_controlnet_weight": 1.0,
            "ad_controlnet_guidance_start": 0.0,
            "ad_controlnet_guidance_end": 1.0
        }
    }
    
    logger.info("Тестовые данные:")
    logger.info(json.dumps(test_data, indent=2, ensure_ascii=False))
    
    try:
        # Проверка доступности сервера
        logger.info("Проверка доступности сервера...")
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.get(f"{base_url}/docs")
                logger.info(f"Сервер доступен. Статус: {response.status_code}")
            except Exception as e:
                logger.error(f"Сервер недоступен: {e}")
                return
        
        # Отправка запроса на генерацию
        logger.info("Отправка запроса на генерацию...")
        start_time = datetime.now()
        
        async with httpx.AsyncClient(timeout=300.0) as client:  # 5 минут таймаут
            response = await client.post(
                generation_url,
                json=test_data,
                headers={"Content-Type": "application/json"}
            )
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        logger.info(f"Время выполнения запроса: {duration:.2f} секунд")
        logger.info(f"Статус ответа: {response.status_code}")
        logger.info(f"Content-Type: {response.headers.get('content-type', 'Не указан')}")
        logger.info(f"Размер ответа: {len(response.content)} байт")
        
        # Логирование ответа
        if response.status_code == 200:
            content_type = response.headers.get('content-type', '')
            
            if 'application/json' in content_type:
                # JSON ответ
                result = response.json()
                logger.info("УСПЕШНАЯ ГЕНЕРАЦИЯ (JSON)!")
                logger.info(f"Результат: {json.dumps(result, indent=2, ensure_ascii=False)}")
                
                # Проверка наличия файлов
                if "images" in result:
                    for i, image_data in enumerate(result["images"]):
                        logger.info(f"Изображение {i+1}: {image_data}")
                        
                        # Проверка существования файла
                        if "filename" in image_data:
                            file_path = Path(image_data["filename"])
                            if file_path.exists():
                                logger.info(f"Файл существует: {file_path}")
                                logger.info(f"Размер файла: {file_path.stat().st_size} байт")
                            else:
                                logger.warning(f"Файл не найден: {file_path}")
                
                # Проверка параметров генерации
                if "generation_params" in result:
                    logger.info("Параметры генерации:")
                    logger.info(json.dumps(result["generation_params"], indent=2, ensure_ascii=False))
                
                # Проверка параметров ADetailer
                if "adetailer_params" in result:
                    logger.info("Параметры ADetailer:")
                    logger.info(json.dumps(result["adetailer_params"], indent=2, ensure_ascii=False))
                    
            elif 'image/' in content_type or 'application/octet-stream' in content_type:
                # Бинарный ответ с изображением
                logger.info("УСПЕШНАЯ ГЕНЕРАЦИЯ (БИНАРНЫЕ ДАННЫЕ)!")
                logger.info(f"Тип контента: {content_type}")
                logger.info(f"Размер изображения: {len(response.content)} байт")
                
                # Сохраняем изображение для проверки
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_dir = Path("test_outputs")
                output_dir.mkdir(exist_ok=True)
                
                image_path = output_dir / f"test_generation_{timestamp}.png"
                with open(image_path, 'wb') as f:
                    f.write(response.content)
                
                logger.info(f"Изображение сохранено: {image_path}")
                logger.info(f"Размер файла: {image_path.stat().st_size} байт")
                
            else:
                # Неизвестный тип контента
                logger.warning(f"Неизвестный тип контента: {content_type}")
                logger.info(f"Первые 100 байт ответа: {response.content[:100]}")
                
        else:
            logger.error(f"ОШИБКА ГЕНЕРАЦИИ!")
            logger.error(f"Статус: {response.status_code}")
            logger.error(f"Ответ: {response.text}")
            
            try:
                error_data = response.json()
                logger.error(f"Детали ошибки: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except Exception:
                logger.error(f"Текст ошибки: {response.text}")
    
    except Exception as e:
        logger.error(f"Исключение при тестировании: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
    
    logger.info("=" * 80)
    logger.info("КОНЕЦ ТЕСТА ГЕНЕРАЦИИ ИЗОБРАЖЕНИЙ")
    logger.info("=" * 80)


async def test_simple_generation():
    """Простой тест с минимальными параметрами"""
    
    logger.info("=" * 80)
    logger.info("ПРОСТОЙ ТЕСТ ГЕНЕРАЦИИ")
    logger.info("=" * 80)
    
    base_url = "http://localhost:8000"
    generation_url = f"{base_url}/api/generation/generate"
    
    # Минимальные параметры
    simple_data = {
        "prompt": "cat, high quality",
        "width": 512,
        "height": 512
    }
    
    logger.info("Минимальные параметры:")
    logger.info(json.dumps(simple_data, indent=2, ensure_ascii=False))
    
    try:
        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.post(
                generation_url,
                json=simple_data,
                headers={"Content-Type": "application/json"}
            )
        
        logger.info(f"Статус: {response.status_code}")
        logger.info(f"Content-Type: {response.headers.get('content-type', 'Не указан')}")
        logger.info(f"Размер ответа: {len(response.content)} байт")
        
        if response.status_code == 200:
            content_type = response.headers.get('content-type', '')
            
            if 'application/json' in content_type:
                result = response.json()
                logger.info("УСПЕХ (JSON)!")
                logger.info(f"Результат: {json.dumps(result, indent=2, ensure_ascii=False)}")
            elif 'image/' in content_type or 'application/octet-stream' in content_type:
                logger.info("УСПЕХ (БИНАРНЫЕ ДАННЫЕ)!")
                logger.info(f"Размер изображения: {len(response.content)} байт")
                
                # Сохраняем изображение
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_dir = Path("test_outputs")
                output_dir.mkdir(exist_ok=True)
                
                image_path = output_dir / f"simple_test_{timestamp}.png"
                with open(image_path, 'wb') as f:
                    f.write(response.content)
                
                logger.info(f"Изображение сохранено: {image_path}")
            else:
                logger.warning(f"Неизвестный тип контента: {content_type}")
        else:
            logger.error(f"Ошибка: {response.text}")
    
    except Exception as e:
        logger.error(f"Исключение: {e}")
    
    logger.info("=" * 80)


async def main():
    """Главная функция для запуска тестов"""
    logger.info("Запуск тестов генерации изображений...")
    
    # Сначала простой тест
    await test_simple_generation()
    
    # Затем подробный тест
    await test_generation_with_logging()


if __name__ == "__main__":
    asyncio.run(main()) 