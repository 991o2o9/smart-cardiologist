import time
from typing import Dict, List
import os
from dotenv import load_dotenv

load_dotenv()

# Настройки rate limiting из переменных окружения
RATE_LIMIT = int(os.getenv("RATE_LIMIT", 5))  

class RateLimiter:
    """Rate limiter с sliding window"""
    
    def __init__(self, max_requests: int = RATE_LIMIT, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, List[float]] = {}
    
    def is_allowed(self, identifier: str) -> bool:
        """
        Проверить, разрешен ли запрос
        
        Args:
            identifier: Идентификатор (обычно IP адрес)
            
        Returns:
            bool: True если запрос разрешен, False если превышен лимит
        """
        now = time.time()
        
        # Получаем список запросов для данного идентификатора
        if identifier not in self.requests:
            self.requests[identifier] = []
        
        # Очищаем старые запросы (старше window_seconds)
        self.requests[identifier] = [
            req_time for req_time in self.requests[identifier]
            if now - req_time < self.window_seconds
        ]
        
        # Проверяем, не превышен ли лимит
        if len(self.requests[identifier]) >= self.max_requests:
            return False
        
        # Добавляем текущий запрос
        self.requests[identifier].append(now)
        return True
    
    def get_remaining_requests(self, identifier: str) -> int:
        """
        Получить количество оставшихся запросов
        
        Args:
            identifier: Идентификатор
            
        Returns:
            int: Количество оставшихся запросов
        """
        now = time.time()
        
        if identifier not in self.requests:
            return self.max_requests
        
        # Очищаем старые запросы
        self.requests[identifier] = [
            req_time for req_time in self.requests[identifier]
            if now - req_time < self.window_seconds
        ]
        
        return max(0, self.max_requests - len(self.requests[identifier]))
    
    def get_reset_time(self, identifier: str) -> float:
        """
        Получить время сброса лимита
        
        Args:
            identifier: Идентификатор
            
        Returns:
            float: Время сброса (timestamp)
        """
        if identifier not in self.requests or not self.requests[identifier]:
            return time.time()
        
        # Время сброса = время самого старого запроса + window_seconds
        oldest_request = min(self.requests[identifier])
        return oldest_request + self.window_seconds
    
    def cleanup_expired(self) -> int:
        """
        Очистить истекшие записи
        
        Returns:
            int: Количество удаленных записей
        """
        now = time.time()
        removed_count = 0
        
        for identifier in list(self.requests.keys()):
            original_count = len(self.requests[identifier])
            self.requests[identifier] = [
                req_time for req_time in self.requests[identifier]
                if now - req_time < self.window_seconds
            ]
            
            # Если все запросы истекли, удаляем идентификатор
            if not self.requests[identifier]:
                del self.requests[identifier]
                removed_count += 1
            else:
                removed_count += original_count - len(self.requests[identifier])
        
        return removed_count
    
    def get_stats(self) -> Dict:
        """
        Получить статистику rate limiter
        
        Returns:
            Dict: Статистика
        """
        return {
            "max_requests": self.max_requests,
            "window_seconds": self.window_seconds,
            "active_identifiers": len(self.requests),
            "total_requests": sum(len(reqs) for reqs in self.requests.values()),
            "expired_cleaned": self.cleanup_expired()
        }


rate_limiter = RateLimiter()
