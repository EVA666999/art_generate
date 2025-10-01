#!/usr/bin/env python3
"""
Скрипт для автоматического обновления фотографий персонажей
"""
import os
import json
from pathlib import Path

def update_character_photos():
    """Обновляет JSON файл с фотографиями персонажей"""
    photos_dir = Path("paid_gallery/main_photos")
    character_photos = {}
    
    if photos_dir.exists():
        # Проходим по всем папкам персонажей
        for character_dir in photos_dir.iterdir():
            if character_dir.is_dir():
                character_name = character_dir.name
                photos = []
                
                # Получаем все PNG файлы в папке персонажа
                for photo_file in character_dir.glob("*.png"):
                    photos.append(f"/paid_gallery/main_photos/{character_name}/{photo_file.name}")
                
                # Сортируем фотографии по имени файла
                photos.sort()
                character_photos[character_name] = photos
    
    # Сохраняем в JSON файл
    output_file = Path("frontend/public/character-photos.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(character_photos, f, ensure_ascii=False, indent=2)
    
    print(f"Обновлено {len(character_photos)} персонажей")
    for name, photos in character_photos.items():
        print(f"  {name}: {len(photos)} фотографий")

if __name__ == "__main__":
    update_character_photos()
