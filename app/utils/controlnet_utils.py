from typing import Dict, Any, Optional
import logging
import base64

logger = logging.getLogger(__name__)

class ControlNetManager:
    def __init__(self):
        self.input_image: Optional[str] = None
        self.controlnet_model: str = "control_v11p_sd15_canny"
        self.control_mode: str = "ControlNet is more important"
        self.pixel_perfect: bool = True
        self.low_vram: bool = False
        self.processor_res: int = 512
        self.threshold_a: float = 100
        self.threshold_b: float = 200

    def set_input_image(self, image_base64: str) -> None:
        """Устанавливает входное изображение для ControlNet"""
        self.input_image = image_base64
        logger.info("Установлено входное изображение для ControlNet")

    def has_input_image(self) -> bool:
        """Проверяет наличие входного изображения"""
        return self.input_image is not None

    def get_controlnet_params(self) -> Dict[str, Any]:
        """Возвращает параметры для ControlNet"""
        if not self.input_image:
            return {}

        return {
            "input_image": self.input_image,
            "model": self.controlnet_model,
            "control_mode": self.control_mode,
            "pixel_perfect": self.pixel_perfect,
            "low_vram": self.low_vram,
            "processor_res": self.processor_res,
            "threshold_a": self.threshold_a,
            "threshold_b": self.threshold_b
        }

controlnet_manager = ControlNetManager() 