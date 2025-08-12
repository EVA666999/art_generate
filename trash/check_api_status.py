#!/usr/bin/env python3
"""
Скрипт для проверки статуса API text-generation-webui
"""

import asyncio
import aiohttp
import json
from typing import Dict, Any

async def check_api_status() -> None:
    """Проверяем статус API text-generation-webui"""
    
    base_url = "http://127.0.0.1:7860"
    
    # Проверяем основные endpoints
    endpoints = [
        "/api/v1/model",
        "/api/v1/generate",
        "/api/v1/chat/completions",
        "/"
    ]
    
    async with aiohttp.ClientSession() as session:
        for endpoint in endpoints:
            try:
                url = f"{base_url}{endpoint}"
                print(f"🔍 Проверяем: {url}")
                
                async with session.get(url, timeout=10) as response:
                    print(f"   Статус: {response.status}")
                    print(f"   Content-Type: {response.headers.get('content-type', 'N/A')}")
                    
                    if response.status == 200:
                        try:
                            content = await response.text()
                            if len(content) > 200:
                                print(f"   Содержимое: {content[:200]}...")
                            else:
                                print(f"   Содержимое: {content}")
                        except:
                            print("   Содержимое: Не удалось прочитать")
                    else:
                        print(f"   Ошибка: {response.status}")
                        
            except Exception as e:
                print(f"   ❌ Ошибка: {e}")
            
            print()

if __name__ == "__main__":
    print("🔧 Проверка статуса API text-generation-webui")
    print("=" * 50)
    asyncio.run(check_api_status())
