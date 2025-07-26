#!/usr/bin/env python3
"""
Тест для проверки исправленного ADetailer
"""

import asyncio
import httpx
import json
from pathlib import Path

async def test_adetailer_fix():
    """Тестирует исправленный ADetailer"""
    
    api_url = "http://localhost:8000/api/generation/generate"
    
    test_data = {
        "prompt": "beautiful woman portrait, close up face, detailed eyes",
        "use_default_prompts": True
    }
    
    print("🔄 Тестируем исправленный ADetailer...")
    print(f"📤 Отправляем запрос: {json.dumps(test_data, indent=2)}")
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(api_url, json=test_data)
            
            if response.status_code == 200:
                print("✅ Запрос выполнен успешно!")
                print(f"📊 Размер ответа: {len(response.content)} байт")
                
                # Проверяем заголовки
                headers = response.headers
                print("\n📋 Заголовки ответа:")
                for key, value in headers.items():
                    if key.startswith('X-'):
                        print(f"  {key}: {value}")
                
                # Сохраняем изображение
                output_path = Path("trash/test_adetailer_fixed.png")
                output_path.parent.mkdir(exist_ok=True)
                
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                
                print(f"💾 Изображение сохранено: {output_path}")
                print(f"📏 Размер файла: {output_path.stat().st_size} байт")
                
                # Проверяем размер - должен быть больше из-за Hires.fix
                if output_path.stat().st_size > 500000:  # > 500KB
                    print("✅ Hires.fix работает - изображение большое")
                else:
                    print("⚠️ Hires.fix может не работать - изображение маленькое")
                
            else:
                print(f"❌ Ошибка: {response.status_code}")
                print(f"📄 Ответ: {response.text}")
                
        except Exception as e:
            print(f"❌ Ошибка запроса: {e}")

if __name__ == "__main__":
    asyncio.run(test_adetailer_fix()) 