#!/usr/bin/env python3
"""
МАССОВЫЙ ГЕНЕРАТОР NSFW ИЗОБРАЖЕНИЙ
Генерирует 30 NSFW изображений и сохраняет в trash/nsfw_images
"""
import asyncio
import httpx
import json
import time
import random
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

class NSFWBulkGenerator:
    """Массовый генератор NSFW изображений"""
    
    def __init__(self):
        self.api_url = "http://localhost:8000"
        self.output_dir = Path("trash/nsfw_images")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Статистика
        self.stats = {
            "total_requested": 30,
            "successful": 0,
            "failed": 0,
            "total_time": 0,
            "start_time": None,
            "end_time": None
        }
        
        # NSFW промпты (простые и разнообразные)
        self.nsfw_prompts = [
            "naked woman, beautiful body, photorealistic",
            "topless woman, natural breasts, high quality",
            "nude female, artistic, professional photography",
            "woman without clothes, elegant pose, studio lighting",
            "female nude, tasteful, artistic nude",
            "naked girl, young woman, natural beauty",
            "topless female, beautiful face, soft lighting",
            "nude woman, sensual pose, high resolution",
            "woman undressed, elegant, professional photo",
            "female without clothes, beautiful body, studio",
            "naked female, artistic nude, tasteful",
            "woman topless, natural beauty, soft focus",
            "nude girl, young, beautiful, high quality",
            "female nude, elegant pose, professional",
            "woman naked, beautiful, artistic photography",
            "topless woman, sensual, studio lighting",
            "nude female, tasteful art, high resolution",
            "woman without clothes, beautiful, natural",
            "female nude, elegant, professional photo",
            "naked woman, artistic, tasteful nude",
            "woman topless, beautiful body, soft light",
            "nude female, young, beautiful, studio",
            "woman undressed, elegant pose, professional",
            "female without clothes, artistic, tasteful",
            "naked girl, beautiful, high quality photo",
            "woman nude, sensual, elegant, studio",
            "topless female, natural beauty, soft focus",
            "nude woman, artistic, professional lighting",
            "female naked, beautiful, tasteful art",
            "woman topless, elegant pose, high resolution"
        ]
        
        # Негативные промпты
        self.negative_prompts = [
            "worst quality, low quality, blurry, ugly, deformed",
            "bad anatomy, bad proportions, extra limbs, missing limbs",
            "watermark, text, signature, logo, artist name",
            "censored, mosaic, pixelated, low resolution"
        ]
    
    def log_progress(self, message: str):
        """Логирует прогресс"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}")
    
    def get_random_prompt(self) -> str:
        """Возвращает случайный NSFW промпт"""
        return random.choice(self.nsfw_prompts)
    
    def get_negative_prompt(self) -> str:
        """Возвращает негативный промпт"""
        return ", ".join(self.negative_prompts)
    
    async def generate_single_image(self, index: int) -> Dict[str, Any]:
        """Генерирует одно изображение"""
        prompt = self.get_random_prompt()
        negative_prompt = self.get_negative_prompt()
        
        # Случайные параметры для разнообразия
        settings = {
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "use_default_prompts": False,  # Используем наши промпты
            "steps": random.randint(20, 30),
            "cfg_scale": random.uniform(6.0, 8.0),
            "width": 512,
            "height": 512,
            "seed": random.randint(1, 999999999)  # Случайный сид
        }
        
        self.log_progress(f"🎨 Генерация {index+1}/30: {prompt[:50]}...")
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                start_time = time.time()
                
                response = await client.post(
                    f"{self.api_url}/api/generation/generate",
                    json=settings,
                    headers={"Content-Type": "application/json"}
                )
                
                generation_time = time.time() - start_time
                
                if response.status_code == 200:
                    # Сохраняем изображение
                    image_data = response.content
                    filename = f"nsfw_{index+1:02d}_{int(time.time())}.png"
                    filepath = self.output_dir / filename
                    
                    with open(filepath, "wb") as f:
                        f.write(image_data)
                    
                    # Получаем информацию из заголовков
                    headers = response.headers
                    result = {
                        "success": True,
                        "filename": filename,
                        "filepath": str(filepath),
                        "file_size": len(image_data),
                        "generation_time": generation_time,
                        "prompt": prompt,
                        "seed": headers.get("X-Seed", "unknown"),
                        "steps": headers.get("X-Steps", "unknown"),
                        "cfg_scale": headers.get("X-CFG-Scale", "unknown"),
                        "sampler": headers.get("X-Sampler", "unknown")
                    }
                    
                    self.log_progress(f"✅ Успешно: {filename} ({len(image_data)} байт, {generation_time:.1f}с)")
                    return result
                    
                else:
                    error_msg = f"HTTP {response.status_code}: {response.text}"
                    self.log_progress(f"❌ Ошибка: {error_msg}")
                    return {
                        "success": False,
                        "error": error_msg,
                        "prompt": prompt
                    }
                    
        except Exception as e:
            error_msg = str(e)
            self.log_progress(f"❌ Исключение: {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "prompt": prompt
            }
    
    async def generate_bulk_images(self):
        """Генерирует все 30 изображений"""
        print("🚀 ЗАПУСК МАССОВОЙ ГЕНЕРАЦИИ NSFW ИЗОБРАЖЕНИЙ")
        print("=" * 60)
        print(f"📁 Папка сохранения: {self.output_dir.absolute()}")
        print(f"🎯 Цель: 30 изображений")
        print(f"⏰ Начало: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        self.stats["start_time"] = time.time()
        results = []
        
        # Генерируем изображения последовательно
        for i in range(30):
            result = await self.generate_single_image(i)
            results.append(result)
            
            if result["success"]:
                self.stats["successful"] += 1
            else:
                self.stats["failed"] += 1
            
            # Небольшая пауза между генерациями
            if i < 29:  # Не делаем паузу после последнего
                await asyncio.sleep(1)
        
        self.stats["end_time"] = time.time()
        self.stats["total_time"] = self.stats["end_time"] - self.stats["start_time"]
        
        # Генерируем отчет
        self.generate_report(results)
    
    def generate_report(self, results: List[Dict[str, Any]]):
        """Генерирует отчет о генерации"""
        print("\n" + "=" * 60)
        print("📋 ОТЧЕТ О МАССОВОЙ ГЕНЕРАЦИИ")
        print("=" * 60)
        
        # Общая статистика
        print(f"📊 СТАТИСТИКА:")
        print(f"   - Запрошено: {self.stats['total_requested']}")
        print(f"   - Успешно: {self.stats['successful']}")
        print(f"   - Ошибок: {self.stats['failed']}")
        print(f"   - Общее время: {self.stats['total_time']:.1f} сек")
        print(f"   - Среднее время на изображение: {self.stats['total_time']/30:.1f} сек")
        
        if self.stats['successful'] > 0:
            success_rate = (self.stats['successful'] / self.stats['total_requested']) * 100
            print(f"   - Процент успеха: {success_rate:.1f}%")
        
        # Анализ успешных генераций
        successful_results = [r for r in results if r["success"]]
        if successful_results:
            total_size = sum(r["file_size"] for r in successful_results)
            avg_size = total_size / len(successful_results)
            avg_time = sum(r["generation_time"] for r in successful_results) / len(successful_results)
            
            print(f"\n📈 АНАЛИЗ УСПЕШНЫХ ГЕНЕРАЦИЙ:")
            print(f"   - Общий размер: {total_size / (1024*1024):.1f} MB")
            print(f"   - Средний размер файла: {avg_size / 1024:.1f} KB")
            print(f"   - Среднее время генерации: {avg_time:.1f} сек")
        
        # Список файлов
        print(f"\n📁 СОЗДАННЫЕ ФАЙЛЫ:")
        for result in successful_results:
            print(f"   ✅ {result['filename']} ({result['file_size']} байт)")
        
        # Ошибки
        failed_results = [r for r in results if not r["success"]]
        if failed_results:
            print(f"\n❌ ОШИБКИ:")
            for result in failed_results:
                print(f"   ❌ Промпт: {result['prompt'][:50]}...")
                print(f"      Ошибка: {result['error']}")
        
        # Сохраняем отчет в файл
        report_file = self.output_dir / "generation_report.txt"
        with open(report_file, "w", encoding="utf-8") as f:
            f.write("ОТЧЕТ О МАССОВОЙ ГЕНЕРАЦИИ NSFW ИЗОБРАЖЕНИЙ\n")
            f.write("=" * 50 + "\n")
            f.write(f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Успешно: {self.stats['successful']}/30\n")
            f.write(f"Время: {self.stats['total_time']:.1f} сек\n\n")
            
            f.write("СОЗДАННЫЕ ФАЙЛЫ:\n")
            for result in successful_results:
                f.write(f"- {result['filename']}\n")
        
        print(f"\n💾 Отчет сохранен: {report_file}")
        print("=" * 60)
        
        if self.stats['successful'] == 30:
            print("🎉 ВСЕ 30 ИЗОБРАЖЕНИЙ УСПЕШНО СОЗДАНЫ!")
        else:
            print(f"⚠️ Создано {self.stats['successful']}/30 изображений")

async def main():
    """Главная функция"""
    generator = NSFWBulkGenerator()
    await generator.generate_bulk_images()

if __name__ == "__main__":
    asyncio.run(main()) 