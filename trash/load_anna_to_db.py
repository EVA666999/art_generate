#!/usr/bin/env python3
"""
Скрипт для загрузки персонажа Anna в базу данных.
Это позволит использовать Anna в основном интерфейсе чата.
"""

import asyncio
import sys
import os
import requests

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def load_anna_to_db():
    """Загружает персонажа Anna в базу данных."""
    
    print("🔄 Загружаем персонажа Anna в базу данных...")
    
    try:
        # URL для загрузки персонажа
        url = "http://localhost:8000/api/v1/chat/load-file-character/anna"
        
        # Отправляем POST запрос
        response = requests.post(url)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Успешно!")
            print(f"📝 Сообщение: {result['message']}")
            print(f"🆔 ID персонажа: {result['character']['id']}")
            print(f"👤 Имя: {result['character']['name']}")
            print(f"📋 Инструкции: {len(result['character']['instructions'])} символов")
            print(f"🎭 Системный промпт: {len(result['character']['system_prompt'])} символов")
            print(f"📝 Формат ответа: {len(result['character']['response_format'])} символов")
            
            print("\n🎉 Теперь Anna доступна в основном интерфейсе чата!")
            print("🌐 Откройте http://localhost:8000/chat и выберите Anna в селекторе персонажей")
            
        else:
            print(f"❌ Ошибка: {response.status_code}")
            print(f"📄 Ответ: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Не удалось подключиться к серверу")
        print("💡 Убедитесь, что FastAPI сервер запущен на http://localhost:8000")
        
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")

def main():
    """Основная функция."""
    print("=" * 50)
    print("  ЗАГРУЗКА ПЕРСОНАЖА ANNA В БАЗУ ДАННЫХ")
    print("=" * 50)
    print()
    
    # Запускаем асинхронную функцию
    asyncio.run(load_anna_to_db())
    
    print()
    print("=" * 50)

if __name__ == "__main__":
    main()
