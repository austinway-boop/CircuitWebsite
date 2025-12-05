"""
Tests for rate limiter.
CRITICAL: Rate limiting prevents excessive costs and runaway processes.
"""
import pytest
import time
from datetime import datetime, timedelta
from src.rate_limiter import RateLimiter
from src.config import config


class TestRateLimiter:
    """Test rate limiting functionality"""
    
    def test_initialization(self):
        """Test that rate limiter initializes correctly"""
        limiter = RateLimiter()
        
        assert limiter.max_per_minute > 0
        assert limiter.max_per_hour > 0
        assert len(limiter.minute_calls) == 0
        assert len(limiter.hour_calls) == 0
    
    def test_check_limit_initially_allows(self):
        """Test that initial check allows calls"""
        limiter = RateLimiter()
        
        assert limiter.check_limit() is True
    
    def test_record_call(self):
        """Test that calls are recorded"""
        limiter = RateLimiter()
        
        limiter.record_call()
        
        assert len(limiter.minute_calls) == 1
        assert len(limiter.hour_calls) == 1
    
    def test_multiple_calls_within_limit(self):
        """Test that multiple calls within limit are allowed"""
        limiter = RateLimiter()
        
        # Record several calls
        for _ in range(5):
            assert limiter.check_limit() is True
            limiter.record_call()
        
        assert len(limiter.minute_calls) == 5
        assert len(limiter.hour_calls) == 5
    
    def test_minute_limit_enforcement(self):
        """Test that per-minute limit is enforced"""
        limiter = RateLimiter()
        
        # Fill up to the limit
        for _ in range(limiter.max_per_minute):
            limiter.record_call()
        
        # Next call should be blocked
        assert limiter.check_limit() is False
    
    def test_hour_limit_enforcement(self):
        """Test that per-hour limit is enforced"""
        limiter = RateLimiter()
        
        # Fill up to the limit
        for _ in range(limiter.max_per_hour):
            limiter.record_call()
        
        # Next call should be blocked
        assert limiter.check_limit() is False
    
    def test_old_calls_cleanup(self):
        """Test that old calls are cleaned up"""
        limiter = RateLimiter()
        
        # Manually add an old call
        old_time = datetime.now() - timedelta(minutes=2)
        limiter.minute_calls.append(old_time)
        limiter.hour_calls.append(old_time)
        
        # Clean should remove it
        limiter._clean_old_calls()
        
        # Minute call should be gone, hour call should remain
        assert len(limiter.minute_calls) == 0
        assert len(limiter.hour_calls) == 1
    
    def test_get_stats(self):
        """Test statistics retrieval"""
        limiter = RateLimiter()
        
        # Record some calls
        for _ in range(5):
            limiter.record_call()
        
        stats = limiter.get_stats()
        
        assert stats['calls_last_minute'] == 5
        assert stats['calls_last_hour'] == 5
        assert stats['limit_per_minute'] == limiter.max_per_minute
        assert stats['limit_per_hour'] == limiter.max_per_hour
        assert stats['remaining_minute'] == limiter.max_per_minute - 5
        assert stats['remaining_hour'] == limiter.max_per_hour - 5
    
    def test_prevents_infinite_loop(self):
        """
        CRITICAL TEST: Ensure rate limiter prevents infinite loops.
        This is essential for cost control with paid services.
        """
        limiter = RateLimiter()
        
        # Simulate a runaway process
        calls_made = 0
        max_attempts = limiter.max_per_minute + 100  # Try to exceed limit
        
        for _ in range(max_attempts):
            if limiter.check_limit():
                limiter.record_call()
                calls_made += 1
            else:
                # Rate limiter stopped us
                break
        
        # Should have stopped at the limit
        assert calls_made <= limiter.max_per_minute
        
        # Verify we can't make more calls
        assert limiter.check_limit() is False

