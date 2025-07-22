"""
Сервис для контроля качества и количества изображений
"""
import base64
import json
import time
from typing import List, Dict, Any, Optional, Tuple
from io import BytesIO
from PIL import Image
import numpy as np
import httpx
from loguru import logger

from app.config.generation_defaults import DEFAULT_GENERATION_PARAMS


class ImageQualityControl:
    """
    Сервис для контроля качества и количества изображений.
    Использует различные методы для анализа и фильтрации изображений.
    """
    
    def __init__(self, api_url: str):
        """
        :param api_url: URL Stable Diffusion WebUI API
        """
        self.api_url = api_url
        self.client = httpx.AsyncClient(timeout=60.0)
        
    async def analyze_images(self, images: List[str]) -> List[Dict[str, Any]]:
        """
        Анализирует список изображений и возвращает метаданные
        
        :param images: Список base64 изображений
        :return: Список метаданных для каждого изображения
        """
        results = []
        
        for i, img_base64 in enumerate(images):
            try:
                # Декодируем изображение
                img_bytes = base64.b64decode(img_base64)
                img = Image.open(BytesIO(img_bytes))
                
                # Базовый анализ
                analysis = {
                    "index": i,
                    "size": img.size,
                    "mode": img.mode,
                    "format": img.format,
                    "file_size": len(img_bytes),
                    "aspect_ratio": img.size[0] / img.size[1],
                    "pixel_count": img.size[0] * img.size[1],
                    "is_valid": True
                }
                
                # Дополнительные проверки
                analysis.update(await self._perform_quality_checks(img, img_bytes))
                
                results.append(analysis)
                
            except Exception as e:
                logger.error(f"Ошибка при анализе изображения {i}: {e}")
                results.append({
                    "index": i,
                    "is_valid": False,
                    "error": str(e)
                })
        
        return results
    
    async def _perform_quality_checks(self, img: Image.Image, img_bytes: bytes) -> Dict[str, Any]:
        """
        Выполняет проверки качества изображения
        
        :param img: PIL Image объект
        :param img_bytes: Байты изображения
        :return: Словарь с результатами проверок
        """
        checks = {}
        
        # Проверка на пустое изображение
        img_array = np.array(img)
        checks["is_empty"] = np.all(img_array == 0) or np.all(img_array == 255)
        
        # Проверка на монохромность
        if img.mode in ['L', 'LA']:
            checks["is_monochrome"] = True
        else:
            # Проверяем, есть ли цветовые различия
            if len(img_array.shape) == 3:
                color_variance = np.var(img_array, axis=(0, 1))
                checks["is_monochrome"] = np.all(color_variance < 100)
            else:
                checks["is_monochrome"] = True
        
        # Проверка размера файла
        checks["file_size_reasonable"] = 1000 < len(img_bytes) < 10000000  # 1KB - 10MB
        
        # Проверка разрешения
        checks["resolution_ok"] = img.size[0] >= 64 and img.size[1] >= 64
        
        # Проверка на артефакты (простая проверка)
        if len(img_array.shape) == 3:
            # Проверяем на резкие переходы
            gray = np.mean(img_array, axis=2)
            gradient = np.gradient(gray)
            gradient_magnitude = np.sqrt(gradient[0]**2 + gradient[1]**2)
            checks["has_artifacts"] = np.max(gradient_magnitude) > 100
        else:
            checks["has_artifacts"] = False
        
        return checks
    
    async def filter_best_image(self, images: List[str], criteria: Optional[Dict[str, Any]] = None) -> Tuple[int, str]:
        """
        Выбирает лучшее изображение из списка
        
        :param images: Список base64 изображений
        :param criteria: Критерии выбора (опционально)
        :return: (индекс лучшего изображения, base64 изображение)
        """
        if not images:
            raise ValueError("Список изображений пуст")
        
        if len(images) == 1:
            return 0, images[0]
        
        # Анализируем все изображения
        analysis = await self.analyze_images(images)
        
        # Фильтруем валидные изображения
        valid_images = [(i, analysis[i]) for i, data in enumerate(analysis) if data.get("is_valid", False)]
        
        if not valid_images:
            logger.warning("Нет валидных изображений, возвращаем первое")
            return 0, images[0]
        
        # Сортируем по качеству
        scored_images = []
        for idx, data in valid_images:
            score = self._calculate_quality_score(data, criteria)
            scored_images.append((idx, score, data))
        
        # Сортируем по убыванию качества
        scored_images.sort(key=lambda x: x[1], reverse=True)
        
        best_idx = scored_images[0][0]
        logger.info(f"Выбрано изображение {best_idx} с качеством {scored_images[0][1]:.2f}")
        
        return best_idx, images[best_idx]
    
    def _calculate_quality_score(self, analysis: Dict[str, Any], criteria: Optional[Dict[str, Any]] = None) -> float:
        """
        Вычисляет оценку качества изображения
        
        :param analysis: Результаты анализа изображения
        :param criteria: Критерии оценки (опционально)
        :return: Оценка качества (0-100)
        """
        score = 0.0
        
        # Базовые критерии
        if not analysis.get("is_empty", False):
            score += 20
        
        if not analysis.get("is_monochrome", False):
            score += 15
        
        if analysis.get("file_size_reasonable", False):
            score += 10
        
        if analysis.get("resolution_ok", False):
            score += 15
        
        if not analysis.get("has_artifacts", False):
            score += 20
        
        # Дополнительные критерии
        if criteria:
            # Предпочтение определенного размера
            if "preferred_size" in criteria:
                preferred = criteria["preferred_size"]
                actual = analysis["size"]
                size_diff = abs(actual[0] - preferred[0]) + abs(actual[1] - preferred[1])
                if size_diff < 100:
                    score += 10
            
            # Предпочтение определенного соотношения сторон
            if "preferred_aspect_ratio" in criteria:
                preferred = criteria["preferred_aspect_ratio"]
                actual = analysis["aspect_ratio"]
                aspect_diff = abs(actual - preferred)
                if aspect_diff < 0.1:
                    score += 10
        
        return min(score, 100.0)
    
    async def ensure_single_image(self, images: List[str], 
                                force_single: bool = True,
                                quality_threshold: float = 50.0) -> List[str]:
        """
        Обеспечивает возврат только одного изображения
        
        :param images: Список изображений
        :param force_single: Принудительно возвращать только одно изображение
        :param quality_threshold: Порог качества для фильтрации
        :return: Список изображений (обычно один)
        """
        if not images:
            return []
        
        if len(images) == 1:
            return images
        
        logger.info(f"Получено {len(images)} изображений, применяем фильтрацию")
        
        if force_single:
            # Выбираем лучшее изображение
            best_idx, best_image = await self.filter_best_image(images)
            
            # Проверяем качество
            analysis = await self.analyze_images([best_image])
            if analysis and analysis[0].get("is_valid", False):
                quality_score = self._calculate_quality_score(analysis[0])
                if quality_score >= quality_threshold:
                    logger.info(f"Возвращаем лучшее изображение (качество: {quality_score:.2f})")
                    return [best_image]
                else:
                    logger.warning(f"Лучшее изображение не прошло порог качества: {quality_score:.2f}")
            
            # Если качество не прошло, возвращаем первое
            return [images[0]]
        else:
            # Фильтруем по качеству, но можем вернуть несколько
            filtered_images = []
            analysis = await self.analyze_images(images)
            
            for i, data in enumerate(analysis):
                if data.get("is_valid", False):
                    quality_score = self._calculate_quality_score(data)
                    if quality_score >= quality_threshold:
                        filtered_images.append(images[i])
                        logger.info(f"Изображение {i} прошло фильтр (качество: {quality_score:.2f})")
            
            return filtered_images if filtered_images else [images[0]]
    
    async def detect_duplicates(self, images: List[str], similarity_threshold: float = 0.95) -> List[int]:
        """
        Обнаруживает дублирующиеся изображения
        
        :param images: Список изображений
        :param similarity_threshold: Порог схожести
        :return: Индексы дублирующихся изображений
        """
        if len(images) < 2:
            return []
        
        duplicates = []
        
        for i in range(len(images)):
            for j in range(i + 1, len(images)):
                try:
                    similarity = await self._calculate_similarity(images[i], images[j])
                    if similarity > similarity_threshold:
                        duplicates.append(j)
                        logger.info(f"Обнаружен дубликат: изображения {i} и {j} (схожесть: {similarity:.3f})")
                except Exception as e:
                    logger.error(f"Ошибка при сравнении изображений {i} и {j}: {e}")
        
        return list(set(duplicates))
    
    async def _calculate_similarity(self, img1_base64: str, img2_base64: str) -> float:
        """
        Вычисляет схожесть между двумя изображениями
        
        :param img1_base64: Первое изображение в base64
        :param img2_base64: Второе изображение в base64
        :return: Коэффициент схожести (0-1)
        """
        try:
            # Декодируем изображения
            img1_bytes = base64.b64decode(img1_base64)
            img2_bytes = base64.b64decode(img2_base64)
            
            img1 = Image.open(BytesIO(img1_bytes))
            img2 = Image.open(BytesIO(img2_bytes))
            
            # Приводим к одинаковому размеру
            size = (256, 256)  # Уменьшаем для быстрого сравнения
            img1_resized = img1.resize(size)
            img2_resized = img2.resize(size)
            
            # Конвертируем в numpy массивы
            arr1 = np.array(img1_resized.convert('L'))  # В оттенки серого
            arr2 = np.array(img2_resized.convert('L'))
            
            # Вычисляем корреляцию
            correlation = np.corrcoef(arr1.flatten(), arr2.flatten())[0, 1]
            
            return max(0, correlation) if not np.isnan(correlation) else 0
            
        except Exception as e:
            logger.error(f"Ошибка при вычислении схожести: {e}")
            return 0.0
    
    async def close(self):
        """Закрывает клиент"""
        await self.client.aclose()


# Глобальный экземпляр для использования в других сервисах
image_quality_control = None

def get_image_quality_control(api_url: str) -> ImageQualityControl:
    """
    Получает глобальный экземпляр контроллера качества изображений
    
    :param api_url: URL API
    :return: Экземпляр ImageQualityControl
    """
    global image_quality_control
    if image_quality_control is None:
        image_quality_control = ImageQualityControl(api_url)
    return image_quality_control 