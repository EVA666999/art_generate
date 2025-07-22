# — config_generation.py —

import os
from typing import Dict, Any
from app.config.default_prompts import get_default_positive_prompts, get_default_negative_prompts

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# — Настройки LoRA —
LORA_MODELS: Dict[str, Dict[str, Any]] = {
    "face_xl_v0_1.safetensors": {
        "name": "face_xl_v0_1",
        "weight": 1.0,
        "enabled": True,
        "path": os.path.join(BASE_DIR, "models", "Lora", "face_xl_v0_1.safetensors")
    },
    "UltraRealPhoto.safetensors": {
        "name": "UltraRealPhoto",
        "weight": 1.0,
        "enabled": True,
        "path": os.path.join(BASE_DIR, "models", "Lora", "UltraRealPhoto.safetensors")
    }
}

# — Настройки ADetailer —
ADETAILER_SETTINGS: Dict[str, Any] = {
    "ad_model": "face_yolov8n.pt",
    "ad_prompt": "face, portrait, detailed face, beautiful face, perfect face, detailed eyes, perfect eyes",
    "ad_negative_prompt": "bad quality, lowres, text, watermark, signature, blurry",
    "ad_denoising_strength": 0.4,
    "ad_confidence": 0.3,
    "ad_mask_blur": 4,
    "ad_inpaint_only_masked": True,
    "ad_inpaint_only_masked_padding": 32,
    "ad_use_inpaint_width_height": False,
    "ad_inpaint_width": 512,
    "ad_inpaint_height": 512,
    "ad_use_steps": True,
    "ad_steps": 60,
    "ad_use_cfg_scale": True,
    "ad_cfg_scale": 7.0,
    "ad_use_sampler": True,
    "ad_sampler_name": "DPM++ SDE Karras",
    "ad_restore_face": True,
    "ad_use_controlnet": False
}

# — Общие параметры генерации —
DEFAULT_GENERATION_PARAMS = {
    "sampler_name": "DPM++ 2M Karras",
    "scheduler": "Karras",
    "steps": 30,  # Можно увеличить до 40-50 для ещё большей детализации
    "width": 1024,
    "height": 1024,
    "cfg_scale": 7,
    "restore_faces": False,  # Используем ADetailer вместо встроенного
    "batch_size": 1,
    "n_iter": 1,
    "n_samples": 1,  # Принудительно только один сэмпл
    "save_grid": False,
    "enable_hr": False,
    "denoising_strength": 0.5,
    "hr_scale": 1.5,
    "hr_upscaler": "4x-UltraSharp",
    "hr_second_pass_steps": 10,
    "hr_prompt": "",  # Не нужен, если enable_hr=False
    "hr_negative_prompt": "",
    "override_settings": {
        "sd_model_checkpoint": "Realistic Vision V6.0 B1",
        "CLIP_stop_at_last_layers": 2,
        "token_merging_ratio": 0.2,
        "token_merging_ratio_hr": 0.2
    },
    "override_settings_restore_afterwards": True,
    "script_args": [],
    "send_images": True,
    "save_images": False,
    "alwayson_scripts": {
        "ADetailer": {
            "args": [True, {
                "ad_model": "face_yolov8n.pt",
                "prompt": "detailed face, perfect skin, high quality",
                "negative_prompt": "bad anatomy, cropped, blur",
                "ad_denoising_strength": 0.4,
                "ad_confidence": 0.3,
                "ad_mask_blur": 4,
                "ad_inpaint_only_masked": True,
                "ad_inpaint_only_masked_padding": 8,
                "ad_steps": 15,
                "ad_cfg_scale": 6,
                "ad_sampler_name": "DPM++ SDE Karras",
            }]
        }
    },
    "lora_models": {
        "UltraRealPhoto.safetensors": {
            "name": "UltraRealPhoto",
            "weight": 1.0,
            "enabled": True,
            "path": os.path.join(BASE_DIR, "models", "Lora", "UltraRealPhoto.safetensors")
        },
        "face_xl_v0_1.safetensors": {
            "name": "face_xl_v0_1",
            "weight": 0.6,
            "enabled": True,
            "path": os.path.join(BASE_DIR, "models", "Lora", "face_xl_v0_1.safetensors")
        }
    },
    "clip_skip": 1,
    "seed": -1
}
