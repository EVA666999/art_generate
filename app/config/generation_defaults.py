from typing import Dict, Any
import os
from app.config.default_prompts import get_default_negative_prompts, get_default_positive_prompts

# Абсолютный путь к корню проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Настройки LoRA моделей
LORA_MODELS: Dict[str, Dict[str, Any]] = {
    "add_detail.safetensors": {
        "name": "add_detail",
        "weight": 1.0,
        "enabled": True, 
        "path": os.path.join(BASE_DIR, "models", "Lora", "add_detail.safetensors")
    },
    "face_xl_v0_1.safetensors": {
        "name": "face_xl_v0_1",
        "weight": 0.5,
        "enabled": True,
        "path": os.path.join(BASE_DIR, "models", "Lora", "face_xl_v0_1.safetensors")
    },
    # "hyper_lora_modules.safetensors": {
    #     "name": "hyper_lora_modules",
    #     "weight": 0.65,
    #     "enabled": True,
    #     "path": os.path.join(BASE_DIR, "models", "Lora", "hyper_lora_modules.safetensors")
    # },
    "roundassv1.safetensors": {
        "name": "roundassv1",
        "weight": 1.0,
        "enabled": False,
        "path": os.path.join(BASE_DIR, "models", "Lora", "roundassv1.safetensors")
    },
    "UltraRealPhoto.safetensors": {
        "name": "UltraRealPhoto",
        "weight": 1.0,
        "enabled": True,
        "path": os.path.join(BASE_DIR, "models", "Lora", "UltraRealPhoto.safetensors")
    }
}

# Настройки ADetailer
ADETAILER_SETTINGS: Dict[str, Any] = {
    "ad_model": "face_yolov8n.pt",
    "prompt": "face, portrait, detailed face, beautiful face, perfect face, detailed eyes, perfect eyes, detailed skin, perfect skin, 8k uhd, high quality, masterpiece, best quality, extremely detailed",
    "negative_prompt": "bad quality, worst quality, low quality, normal quality, lowres, low details, oversaturated, undersaturated, overexposed, underexposed, grayscale, bw, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, jpeg artifacts, signature, watermark, username, blurry",
    "ad_denoising_strength": 0.4,
    "ad_confidence": 0.3,
    "ad_mask_blur": 4,
    "ad_inpaint_only_masked": True,
    "ad_inpaint_only_masked_padding": 8,
    "ad_use_inpaint_width_height": False,
    "ad_inpaint_width": 512,
    "ad_inpaint_height": 512,
    "ad_use_steps": True,
    "ad_steps": 15,
    "ad_use_cfg_scale": True,
    "ad_cfg_scale": 6,
    "ad_use_sampler": True,
    "ad_sampler_name": "DPM++ SDE Karras",
    "ad_use_noise_multiplier": False,
    "ad_noise_multiplier": 1.0,
    "ad_use_clip_skip": False,
    "ad_clip_skip": 1,
    "ad_restore_face": False,
    "ad_use_controlnet": False,
    "ad_controlnet_model": "None",
    "ad_controlnet_weight": 1.0,
    "ad_controlnet_guidance_start": 0.0,
    "ad_controlnet_guidance_end": 1.0
}

# Дефолтные параметры генерации
DEFAULT_GENERATION_PARAMS: Dict[str, Any] = {
    "sampler_name": "DPM++ SDE Karras",
    "scheduler": "Karras",
    "steps": 35,
    "width": 512,
    "height": 512,
    "cfg_scale": 8,
    "restore_faces": False,
    "batch_size": 1,
    "n_iter": 1,
    "save_grid": False,
    "enable_hr": True,
    "denoising_strength": 0.4,
    "firstphase_width": 0,
    "firstphase_height": 0,
    "hr_scale": 1.9,
    "hr_upscaler": "4x-UltraSharp",
    "hr_second_pass_steps": 10,
    "hr_resize_x": 0,
    "hr_resize_y": 0,
    "hr_sampler_name": "DPM++ SDE Karras",
    "hr_prompt": get_default_positive_prompts(),
    "hr_negative_prompt": get_default_negative_prompts(),
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
            "args": [True, ADETAILER_SETTINGS]
        }
    },
    "lora_models": {
        k: v for k, v in LORA_MODELS.items() if v.get("enabled", True)
    },
    "clip_skip": 1,
    "seed": -1
}