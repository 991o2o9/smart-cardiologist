"""
Unit тесты для кеша
"""
import pytest
import time
from src.utils.cache import Cache


class TestCache:
    """Тесты для класса Cache"""
    
    def test_cache_set_get(self):
        """Тест установки и получения значения"""
        cache = Cache(ttl=10)
        cache.set("test_key", "test_value")
        
        assert cache.get("test_key") == "test_value"
    
    def test_cache_expiration(self):
        """Тест истечения срока действия кеша"""
        cache = Cache(ttl=0.1)  # 100ms
        cache.set("test_key", "test_value")
        
        # Значение должно быть доступно сразу
        assert cache.get("test_key") == "test_value"
        
        # Ждем истечения
        time.sleep(0.2)
        
        # Значение должно быть удалено
        assert cache.get("test_key") is None
    
    def test_cache_clear(self):
        """Тест очистки кеша"""
        cache = Cache()
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        
        assert cache.size() == 2
        
        cache.clear()
        assert cache.size() == 0
    
    def test_cache_stats(self):
        """Тест статистики кеша"""
        cache = Cache(ttl=10)
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        
        stats = cache.get_stats()
        
        assert stats["size"] == 2
        assert stats["ttl"] == 10
        assert "expired_cleaned" in stats
    
    def test_cache_cleanup_expired(self):
        """Тест очистки истекших записей"""
        cache = Cache(ttl=0.1)  # 100ms
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        
        # Ждем истечения
        time.sleep(0.2)
        
        # Очищаем истекшие
        cleaned_count = cache.cleanup_expired()
        
        assert cleaned_count == 2
        assert cache.size() == 0
