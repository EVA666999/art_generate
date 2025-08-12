"""
Настройки по умолчанию для генерации изображений Stable Diffusion.
"""

from typing import Dict, Any, List

# Основные параметры генерации по умолчанию
DEFAULT_GENERATION_PARAMS = {
    "sampler_name": "DPM++ 2M Karras",
    "steps": 35,
    "width": 512,
    "height": 853,
    "cfg_scale": 7.0,
    "restore_faces": False,
    "batch_size": 1,
    "n_iter": 1,
    "n_samples": 1,
    "save_grid": False,
    "enable_hr": True,
    "denoising_strength": 0.5,
    "hr_scale": 1.5,
    "hr_upscaler": "R-ESRGAN 4x+ Anime6B",
    "hr_second_pass_steps": 10,
    "hr_prompt": "",
    "hr_negative_prompt": "",
    "override_settings": {},
    "override_settings_restore_afterwards": False,
    "script_args": [],
    "send_images": True,
    "save_images": False,
    "alwayson_scripts": {
        "ADetailer": {
            "args": [
                {
                    "ad_model": "face_yolov8n.pt",
                    "ad_steps": 10,
                    "ad_denoising_strength": 0.5,
                    "ad_cfg_scale": 8,
                    "ad_mask_blur": 3,
                    "ad_inpaint_only_masked": True,
                    "ad_inpaint_only_masked_padding": 24,
                    "ad_confidence": 0.2,
                    "ad_dilate_erode": 2,
                    "ad_use_steps": True,
                    "ad_use_cfg_scale": True,
                    "ad_prompt": ("anime style face, clean line art, symmetrical eyes, "
                                 "glossy eyes, sharp anime details, perfect anime face"),
                    "ad_negative_prompt": ("deformed face, wonky eyes, double irises, "
                                          "bad symmetry, lowres, blurry")
                },
                {
                    "ad_model": "hand_yolov9c.pt",
                    "ad_steps": 40,
                    "ad_denoising_strength": 0.3,
                    "ad_cfg_scale": 8,
                    "ad_mask_blur": 4,
                    "ad_inpaint_only_masked": True,
                    "ad_inpaint_only_masked_padding": 32,
                    "ad_confidence": 0.3,
                    "ad_dilate_erode": 4,
                    "ad_use_steps": True,
                    "ad_use_cfg_scale": True,
                    "ad_prompt": ("perfect hands, detailed fingers, natural hand anatomy"),
                    "ad_negative_prompt": ("deformed hands, extra fingers, missing fingers, "
                                          "bad anatomy, mutated hands, ugly hands")
                }
            ]
        }
    },
    "lora_models": [
        {
            "name": "pastel-anime-xl-latest",
            "weight": 0.4,
            "enabled": False
        },
        {
            "name": "DetailedEyes_V3",
            "weight": 0.6,
            "enabled": False
        },
        {
            "name": "1.5_perfect hands",
            "weight": 0.8,
            "enabled": True
        },
        {
            "name": "add_detail",
            "weight": 0.5,
            "enabled": True
        },
        {
            "name": "easynegative.safetensors",
            "weight": 1.0,
            "enabled": True
        },
    ],
    "clip_skip": 2,
    "seed": -1,
}

# Параметры для разных типов генерации
ANIME_GENERATION_PARAMS = {
    **DEFAULT_GENERATION_PARAMS,
    "width": 512,
    "height": 768,
    "cfg_scale": 7.5,
    "steps": 40,
}

REALISTIC_GENERATION_PARAMS = {
    **DEFAULT_GENERATION_PARAMS,
    "width": 512,
    "height": 512,
    "cfg_scale": 8.0,
    "steps": 50,
    "restore_faces": True,
}

# Параметры для ADetailer
ADETAILER_FACE_PARAMS = {
    "ad_model": "face_yolov8n.pt",
    "ad_steps": 10,
    "ad_denoising_strength": 0.5,
    "ad_cfg_scale": 8,
    "ad_mask_blur": 3,
    "ad_inpaint_only_masked": True,
    "ad_inpaint_only_masked_padding": 24,
    "ad_confidence": 0.2,
    "ad_dilate_erode": 2,
    "ad_use_steps": True,
    "ad_use_cfg_scale": True,
    "ad_prompt": ("anime style face, clean line art, symmetrical eyes, "
                   "glossy eyes, sharp anime details, perfect anime face"),
    "ad_negative_prompt": ("deformed face, wonky eyes, double irises, "
                           "bad symmetry, lowres, blurry")
}

ADETAILER_HAND_PARAMS = {
    "ad_model": "hand_yolov9c.pt",
    "ad_steps": 40,
    "ad_denoising_strength": 0.3,
    "ad_cfg_scale": 8,
    "ad_mask_blur": 4,
    "ad_inpaint_only_masked": True,
    "ad_inpaint_only_masked_padding": 32,
    "ad_confidence": 0.3,
    "ad_dilate_erode": 4,
    "ad_use_steps": True,
    "ad_use_cfg_scale": True,
    "ad_prompt": ("perfect hands, detailed fingers, natural hand anatomy"),
    "ad_negative_prompt": ("deformed hands, extra fingers, missing fingers, "
                           "bad anatomy, mutated hands, ugly hands")
}

# LoRA модели
LORA_MODELS = {
    "pastel-anime-xl-latest": {
        "name": "pastel-anime-xl-latest",
        "weight": 0.4,
        "enabled": False
    },
    "DetailedEyes_V3": {
        "name": "DetailedEyes_V3",
        "weight": 0.6,
        "enabled": False
    },
    "1.5_perfect hands": {
        "name": "1.5_perfect hands",
        "weight": 0.8,
        "enabled": True
    },
    "add_detail": {
        "name": "add_detail",
        "weight": 0.5,
        "enabled": True
    },
    "easynegative": {
        "name": "easynegative.safetensors",
        "weight": 1.0,
        "enabled": True
    },
}

def get_generation_params(
    preset: str = "default",
    custom_params: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Получить параметры генерации по умолчанию.
    
    Args:
        preset: Предустановка параметров ("default", "anime", "realistic")
        custom_params: Дополнительные параметры для переопределения
        
    Returns:
        Словарь с параметрами генерации
    """
    if preset == "anime":
        base_params = ANIME_GENERATION_PARAMS.copy()
    elif preset == "realistic":
        base_params = REALISTIC_GENERATION_PARAMS.copy()
    else:
        base_params = DEFAULT_GENERATION_PARAMS.copy()
    
    if custom_params:
        base_params.update(custom_params)
    
    return base_params

def get_adetailer_params(
    face_params: Dict[str, Any] = None,
    hand_params: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Получить параметры для ADetailer.
    
    Args:
        face_params: Параметры для обработки лиц
        hand_params: Параметры для обработки рук
        
    Returns:
        Словарь с параметрами ADetailer
    """
    adetailer_config = {
        "ADetailer": {
            "args": []
        }
    }
    
    if face_params:
        adetailer_config["ADetailer"]["args"].append({
            **ADETAILER_FACE_PARAMS,
            **face_params
        })
    
    if hand_params:
        adetailer_config["ADetailer"]["args"].append({
            **ADETAILER_HAND_PARAMS,
            **hand_params
        })
    
    return adetailer_config
