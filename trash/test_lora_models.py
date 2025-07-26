#!/usr/bin/env python3
"""
Тест применения LoRA моделей
"""
import asyncio
import httpx
import json
import time
from pathlib import Path

async def test_lora_models():
    api_url = "http://localhost:8000/api/generation/generate"
    
    test_data = {
        "prompt": "beautiful woman portrait, close up face, detailed eyes, high quality, UltraRealPhoto style",
        "use_default_prompts": True
    }
    
    print("🔍 ТЕСТ ПРИМЕНЕНИЯ LoRA МОДЕЛЕЙ")
    print("=" * 50)
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            start_time = time.time()
            print("🔄 Отправляем запрос...")
            
            response = await client.post(api_url, json=test_data)
            
            end_time = time.time()
            generation_time = end_time - start_time
            
            print(f"⏱️ Время генерации: {generation_time:.2f} секунд")
            
            if response.status_code == 200:
                print("✅ Запрос выполнен успешно!")
                
                # Сохраняем изображение
                output_path = Path("trash/lora_models_test.png")
                output_path.parent.mkdir(exist_ok=True)
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                
                file_size = output_path.stat().st_size
                print(f"💾 Изображение сохранено: {output_path}")
                print(f"📏 Размер файла: {file_size:,} байт")
                
                # Анализируем заголовки
                headers = response.headers
                print("\n📋 ЗАГОЛОВКИ ОТВЕТА:")
                for key, value in headers.items():
                    if key.startswith('X-'):
                        print(f"  {key}: {value}")
                
                # Проверяем качество
                if generation_time > 40:
                    print("✅ Время генерации нормальное")
                else:
                    print("⚠️ Генерация быстрая")
                
                if file_size > 500000:
                    print("✅ Размер файла нормальный")
                else:
                    print("⚠️ Файл маленький")
                
                print("\n📊 ОЖИДАЕМЫЕ LoRA МОДЕЛИ:")
                print("   - UltraRealPhoto.safetensors (weight: 1.0)")
                print("   - face_xl_v0_1.safetensors (weight: 1.0)")
                    
            else:
                print(f"❌ Ошибка: {response.status_code}")
                print(f"Ответ: {response.text}")
                
        except Exception as e:
            print(f"❌ Ошибка запроса: {e}")

if __name__ == "__main__":
    asyncio.run(test_lora_models()) 