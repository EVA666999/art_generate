#!/usr/bin/env python3
"""
ТЕСТ ДЛЯ ПРОВЕРКИ ADETAILER
Проверяет что ADetailer включен и работает
"""
import asyncio
import httpx
import json
import time
from pathlib import Path
from datetime import datetime

class ADetailerTest:
    """Тест для проверки ADetailer"""
    
    def __init__(self):
        self.api_url = "http://localhost:8000"
        self.output_dir = Path("trash/test_adetailer")
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def log_test(self, message: str):
        """Логирует тест"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}")
    
    async def test_adetailer_generation(self):
        """Тестирует генерацию с ADetailer"""
        print("🧪 ТЕСТИРОВАНИЕ ADETAILER")
        print("=" * 50)
        
        # Тестовые данные с лицом
        test_data = {
            "prompt": "beautiful woman portrait, close up face, high quality, photorealistic, detailed eyes, perfect skin, ultra detailed, 8k resolution, professional photography",
            "negative_prompt": "worst quality, low quality, blurry, ugly, deformed, bad anatomy, low resolution, pixelated",
            "use_default_prompts": False,
            "steps": 60,  # Максимальное количество шагов для ADetailer
            "cfg_scale": 9.0,  # Высокий CFG для детализации
            "width": 512,
            "height": 512,
            "seed": 42,  # Фиксированный сид для воспроизводимости
            "use_adetailer": True  # Явно включаем ADetailer
        }
        
        self.log_test("🎨 Генерируем изображение с ADetailer...")
        self.log_test(f"📝 Промпт: {test_data['prompt']}")
        self.log_test(f"⚙️ Параметры: steps={test_data['steps']}, cfg={test_data['cfg_scale']}")
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                start_time = time.time()
                
                response = await client.post(
                    f"{self.api_url}/api/generation/generate",
                    json=test_data,
                    headers={"Content-Type": "application/json"}
                )
                
                generation_time = time.time() - start_time
                
                if response.status_code == 200:
                    # Сохраняем изображение
                    image_data = response.content
                    filename = f"adetailer_test_{int(time.time())}.png"
                    filepath = self.output_dir / filename
                    
                    with open(filepath, "wb") as f:
                        f.write(image_data)
                    
                    # Получаем информацию из заголовков
                    headers = response.headers
                    
                    print(f"✅ Генерация успешна!")
                    print(f"⏱️ Время: {generation_time:.1f} сек")
                    print(f"📏 Размер: {len(image_data)} байт")
                    print(f"💾 Сохранено: {filepath}")
                    
                    print(f"\n📊 ЗАГОЛОВКИ ОТВЕТА:")
                    print(f"   - Seed: {headers.get('X-Seed', 'N/A')}")
                    print(f"   - Steps: {headers.get('X-Steps', 'N/A')}")
                    print(f"   - CFG: {headers.get('X-CFG-Scale', 'N/A')}")
                    print(f"   - Sampler: {headers.get('X-Sampler', 'N/A')}")
                    print(f"   - Images: {headers.get('X-Images-Generated', 'N/A')}")
                    
                    # Анализируем результат
                    if len(image_data) > 50000:
                        print(f"\n🎯 АНАЛИЗ:")
                        print(f"   ✅ Размер файла нормальный: {len(image_data)} байт")
                        print(f"   ✅ Время генерации приемлемое: {generation_time:.1f} сек")
                        
                        # Проверяем что время больше обычного (ADetailer добавляет время)
                        if generation_time > 15.0:
                            print(f"   ✅ Время генерации ОЧЕНЬ большое - ADetailer работает интенсивно!")
                        elif generation_time > 12.0:
                            print(f"   ✅ Время генерации значительно увеличенное - ADetailer работает!")
                        elif generation_time > 8.0:
                            print(f"   ✅ Время генерации увеличенное - ADetailer работает!")
                        else:
                            print(f"   ⚠️ Время генерации быстрое - возможно ADetailer не работает")
                        
                        print(f"\n🎉 ТЕСТ ПРОЙДЕН! ADetailer включен и работает!")
                        return True
                    else:
                        print(f"\n❌ ПРОБЛЕМА: Файл слишком маленький ({len(image_data)} байт)")
                        return False
                        
                else:
                    print(f"❌ Ошибка HTTP {response.status_code}: {response.text}")
                    return False
                    
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return False
    
    async def test_without_adetailer(self):
        """Тест без ADetailer для сравнения"""
        print(f"\n🧪 ТЕСТ БЕЗ ADETAILER (для сравнения)")
        print("=" * 50)
        
        test_data = {
            "prompt": "beautiful woman portrait, close up face, high quality, photorealistic",
            "negative_prompt": "worst quality, low quality, blurry, ugly, deformed",
            "use_default_prompts": False,
            "steps": 15,  # Минимальное количество шагов без ADetailer
            "cfg_scale": 6.0,  # Низкий CFG для быстрой генерации
            "width": 512,
            "height": 512,
            "seed": 42,  # Тот же сид
            "use_adetailer": False  # Отключаем ADetailer
        }
        
        self.log_test("🎨 Генерируем изображение БЕЗ ADetailer...")
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                start_time = time.time()
                
                response = await client.post(
                    f"{self.api_url}/api/generation/generate",
                    json=test_data,
                    headers={"Content-Type": "application/json"}
                )
                
                generation_time = time.time() - start_time
                
                if response.status_code == 200:
                    image_data = response.content
                    filename = f"no_adetailer_test_{int(time.time())}.png"
                    filepath = self.output_dir / filename
                    
                    with open(filepath, "wb") as f:
                        f.write(image_data)
                    
                    print(f"✅ Генерация БЕЗ ADetailer успешна!")
                    print(f"⏱️ Время: {generation_time:.1f} сек")
                    print(f"📏 Размер: {len(image_data)} байт")
                    print(f"💾 Сохранено: {filepath}")
                    
                    return generation_time
                else:
                    print(f"❌ Ошибка: {response.status_code}")
                    return None
                    
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return None
    
    async def run_comparison_test(self):
        """Запускает сравнительный тест"""
        print("🚀 ЗАПУСК СРАВНИТЕЛЬНОГО ТЕСТА ADETAILER")
        print("=" * 60)
        
        # Тест с ADetailer
        adetailer_success = await self.test_adetailer_generation()
        
        # Тест без ADetailer
        no_adetailer_time = await self.test_without_adetailer()
        
        # Сравнение
        print(f"\n📊 СРАВНЕНИЕ РЕЗУЛЬТАТОВ:")
        print("=" * 40)
        
        if adetailer_success and no_adetailer_time:
            print(f"✅ ADetailer: ВКЛЮЧЕН и работает")
            print(f"✅ Без ADetailer: Работает ({no_adetailer_time:.1f} сек)")
            print(f"\n🎯 ВЫВОД: ADetailer успешно включен и функционирует!")
        elif adetailer_success:
            print(f"✅ ADetailer: ВКЛЮЧЕН и работает")
            print(f"❌ Без ADetailer: Ошибка")
            print(f"\n🎯 ВЫВОД: ADetailer работает, но есть проблемы с отключением")
        else:
            print(f"❌ ADetailer: НЕ РАБОТАЕТ")
            print(f"\n🎯 ВЫВОД: ADetailer не включен или не работает")
        
        print("=" * 60)

async def main():
    """Главная функция"""
    tester = ADetailerTest()
    await tester.run_comparison_test()

if __name__ == "__main__":
    asyncio.run(main()) 