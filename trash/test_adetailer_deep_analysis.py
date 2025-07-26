#!/usr/bin/env python3
"""
Глубокий анализ ADetailer - проверка всех параметров
"""
import asyncio
import httpx
import json
import time
from pathlib import Path

async def test_adetailer_deep_analysis():
    api_url = "http://localhost:8000/api/generation/generate"
    
    # Тест с простым промптом для лица
    test_data = {
        "prompt": "beautiful woman portrait, close up face, detailed eyes, high quality",
        "use_default_prompts": True
    }
    
    print("🔍 ГЛУБОКИЙ АНАЛИЗ ADETAILER")
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
                output_path = Path("trash/adetailer_deep_analysis.png")
                output_path.parent.mkdir(exist_ok=True)
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                
                file_size = output_path.stat().st_size
                print(f"💾 Изображение сохранено: {output_path}")
                print(f"📏 Размер файла: {file_size:,} байт")
                
                # Анализируем заголовки
                headers = response.headers
                print("\n📋 АНАЛИЗ ЗАГОЛОВКОВ:")
                for key, value in headers.items():
                    if key.startswith('X-'):
                        print(f"  {key}: {value}")
                
                # Проверяем качество
                if generation_time < 30:
                    print("⚠️ Генерация слишком быстрая - возможно ADetailer не работает")
                else:
                    print("✅ Время генерации нормальное - ADetailer может работать")
                
                if file_size < 500000:
                    print("⚠️ Файл слишком маленький - возможно Hires.fix не работает")
                else:
                    print("✅ Размер файла нормальный - Hires.fix работает")
                    
            else:
                print(f"❌ Ошибка: {response.status_code}")
                print(f"Ответ: {response.text}")
                
        except Exception as e:
            print(f"❌ Ошибка запроса: {e}")

if __name__ == "__main__":
    asyncio.run(test_adetailer_deep_analysis()) 