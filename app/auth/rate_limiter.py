"""
Rate limiter для ограничения частоты запросов.
"""

import time
from typing import Dict, Optional
from fastapi import HTTPException, Request


class RateLimiter:
    """Простой rate limiter на основе времени."""
    
    def __init__(self, max_requests: int = 5, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, list] = {}
    
    def is_allowed(self, key: str) -> bool:
        """Проверяет, разрешен ли запрос."""
        now = time.time()
        
        # Очищаем старые запросы
        if key in self.requests:
            self.requests[key] = [
                req_time for req_time in self.requests[key]
                if now - req_time < self.window_seconds
            ]
        else:
            self.requests[key] = []
        
        # Проверяем лимит
        if len(self.requests[key]) >= self.max_requests:
            return False
        
        # Добавляем текущий запрос
        self.requests[key].append(now)
        return True


# Глобальный экземпляр rate limiter
rate_limiter = RateLimiter(max_requests=10, window_seconds=60)


def get_rate_limiter() -> RateLimiter:
    """Получить экземпляр rate limiter."""
    return rate_limiter
