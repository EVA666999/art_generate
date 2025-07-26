import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# — Общие параметры генерации —
DEFAULT_GENERATION_PARAMS = {
    "sampler_name": "DPM++ 2M Karras",
                  "steps": 60,  # Стандартные шаги + ADetailer 30 шагов
    "width": 512,
    "height": 512,
    "cfg_scale": 7,
    "restore_faces": False,  # Используем ADetailer вместо встроенного
    "batch_size": 1,
    "n_iter": 1,
    "n_samples": 1,  # Принудительно только один сэмпл
    "save_grid": False,
    "enable_hr": True,
    "denoising_strength": 0.4,
    "hr_scale": 2,
    "hr_upscaler": "4x-UltraSharp",
    "hr_second_pass_steps": 20,
    "hr_prompt": "",  # Не нужен, если enable_hr=False
    "hr_negative_prompt": "",
    "eta_noise_seed_delta": 31337,  # ENSD для консистентности генерации
    "override_settings": {
        "sd_model_checkpoint": "Realistic Vision V6.0 B1",
        "CLIP_stop_at_last_layers": 1,
        "token_merging_ratio": 0.0,
        "token_merging_ratio_hr": 0.0
    },
    "override_settings_restore_afterwards": False,
    "script_args": [],
    "send_images": True,
    "save_images": False,
                  "alwayson_scripts": {
                  "ADetailer": {
                                              "args": [{
                            "ad_model": "face_yolov8n.pt",
                            "ad_steps": 80,                    # Использовать «отдельные» шаги ADetailer
                            "ad_denoising_strength": 0.5,      # Баланс между сохранением деталей и «чистотой» доработки
                            "ad_cfg_scale": 7.0,               # Влияние промпта ADetailer на конечный результат
                            "ad_mask_blur": 4,                 # Сглаживание границ маски
                            "ad_inpaint_only_masked": True,    # Обрабатывать только саму маску
                            "ad_inpaint_only_masked_padding": 32,  # Отступ вокруг маски (для более плавного перехода)
                            "ad_confidence": 0.3,              # Порог уверенности детектора
                            "ad_dilate_erode": 4,              # Расширение/сужение маски (исправлено название)
                            "ad_use_steps": True,              # Использовать заданные шаги
                            "ad_use_cfg_scale": True,          # Использовать заданный CFG scale
                            "ad_prompt": "face, detailed face",
                            "ad_negative_prompt": "bad anatomy, low quality, blurry, deformed"
                        }]
                  }
              },
    "lora_models": {
        "UltraRealPhoto.safetensors": {
            "name": "UltraRealPhoto",
            "weight": 0.6,
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