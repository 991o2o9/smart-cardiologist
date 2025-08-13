"""
Unit тесты для rate limiter
"""
import pytest
import time
from src.utils.rate_limiter import RateLimiter


class TestRateLimiter:
    """Тесты для класса RateLimiter"""
    
    def test_rate_limiter_initial_state(self):
        """Тест начального состояния"""
        limiter = RateLimiter(max_requests=3, window_seconds=60)
        
        assert limiter.is_allowed("test_ip") == True
        assert limiter.get_remaining_requests("test_ip") == 2
    
    def test_rate_limiter_limit_reached(self):
        """Тест достижения лимита"""
        limiter = RateLimiter(max_requests=2, window_seconds=60)
        
        # Первые два запроса должны быть разрешены
        assert limiter.is_allowed("test_ip") == True
        assert limiter.is_allowed("test_ip") == True
        
        # Третий запрос должен быть заблокирован
        assert limiter.is_allowed("test_ip") == False
    
    def test_rate_limiter_remaining_requests(self):
        """Тест подсчета оставшихся запросов"""
        limiter = RateLimiter(max_requests=5, window_seconds=60)
        
        # Начальное состояние
        assert limiter.get_remaining_requests("test_ip") == 5
        
        # После одного запроса
        limiter.is_allowed("test_ip")
        assert limiter.get_remaining_requests("test_ip") == 4
    
    def test_rate_limiter_window_expiration(self):
        """Тест истечения окна времени"""
        limiter = RateLimiter(max_requests=1, window_seconds=0.1)  # 100ms
        
        # Первый запрос разрешен
        assert limiter.is_allowed("test_ip") == True
        
        # Второй запрос заблокирован
        assert limiter.is_allowed("test_ip") == False
        
        # Ждем истечения окна
        time.sleep(0.2)
        
        # Теперь запрос снова должен быть разрешен
        assert limiter.is_allowed("test_ip") == True
    
    def test_rate_limiter_multiple_identifiers(self):
        """Тест работы с несколькими идентификаторами"""
        limiter = RateLimiter(max_requests=2, window_seconds=60)
        
        # Разные IP должны иметь отдельные лимиты
        assert limiter.is_allowed("ip1") == True
        assert limiter.is_allowed("ip2") == True
        
        assert limiter.get_remaining_requests("ip1") == 1
        assert limiter.get_remaining_requests("ip2") == 1
    
    def test_rate_limiter_stats(self):
        """Тест статистики rate limiter"""
        limiter = RateLimiter(max_requests=3, window_seconds=60)
        
        limiter.is_allowed("ip1")
        limiter.is_allowed("ip2")
        
        stats = limiter.get_stats()
        
        assert stats["max_requests"] == 3
        assert stats["window_seconds"] == 60
        assert stats["active_identifiers"] == 2
        assert stats["total_requests"] == 2
    
    def test_rate_limiter_cleanup(self):
        """Тест очистки истекших записей"""
        limiter = RateLimiter(max_requests=1, window_seconds=0.1)  # 100ms
        
        limiter.is_allowed("ip1")
        limiter.is_allowed("ip2")
        
        # Ждем истечения
        time.sleep(0.2)
        
        # Очищаем истекшие
        cleaned_count = limiter.cleanup_expired()
        
        assert cleaned_count >= 2  # Должно быть очищено минимум 2 записи
