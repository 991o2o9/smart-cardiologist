import time
from typing import Dict, Any, Optional
import os
from dotenv import load_dotenv

load_dotenv()

# Настройки кеша из переменных окружения
CACHE_TTL = int(os.getenv("CACHE_TTL", 300))  # 5 минут по умолчанию

class Cache:
    """Простой in-memory кеш с TTL"""
    
    def __init__(self, ttl: int = CACHE_TTL):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.ttl = ttl
    
    def get(self, key: str) -> Optional[Any]:
        """Получить значение из кеша"""
        if key in self.cache:
            cache_entry = self.cache[key]
            if time.time() - cache_entry["time"] < self.ttl:
                return cache_entry["data"]
            else:
                # Удаляем истекший кеш
                del self.cache[key]
        return None
    
    def set(self, key: str, data: Any) -> None:
        """Сохранить значение в кеш"""
        self.cache[key] = {
            "time": time.time(),
            "data": data
        }
    
    def clear(self) -> None:
        """Очистить весь кеш"""
        self.cache.clear()
    
    def cleanup_expired(self) -> int:
        """Очистить истекшие записи и вернуть количество удаленных"""
        now = time.time()
        expired_keys = [
            key for key, entry in self.cache.items()
            if now - entry["time"] >= self.ttl
        ]
        
        for key in expired_keys:
            del self.cache[key]
        
        return len(expired_keys)
    
    def size(self) -> int:
        """Получить размер кеша"""
        return len(self.cache)
    
    def get_stats(self) -> Dict[str, Any]:
        """Получить статистику кеша"""
        return {
            "size": self.size(),
            "ttl": self.ttl,
            "expired_cleaned": self.cleanup_expired()
        }


cache = Cache()
