"""
Rate Limiter
Implements rate limiting to prevent excessive API calls and control costs.
CRITICAL: Prevents infinite loops and runaway costs with paid services.
"""
import time
from collections import deque
from datetime import datetime, timedelta
import logging
from .config import config

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Rate limiter with per-minute and per-hour limits.
    
    SECURITY: This prevents:
    - Infinite loops that could drain API quotas
    - Accidental runaway processes
    - Excessive costs from paid API services
    """
    
    def __init__(self):
        """Initialize rate limiter with configured limits"""
        self.max_per_minute = config.max_api_calls_per_minute
        self.max_per_hour = config.max_api_calls_per_hour
        
        # Use deques for efficient time-window tracking
        self.minute_calls = deque()
        self.hour_calls = deque()
        
        logger.info(
            f"Rate limiter initialized: "
            f"{self.max_per_minute}/min, {self.max_per_hour}/hour"
        )
    
    def _clean_old_calls(self):
        """Remove calls outside the time windows"""
        now = datetime.now()
        minute_ago = now - timedelta(minutes=1)
        hour_ago = now - timedelta(hours=1)
        
        # Remove calls older than 1 minute
        while self.minute_calls and self.minute_calls[0] < minute_ago:
            self.minute_calls.popleft()
        
        # Remove calls older than 1 hour
        while self.hour_calls and self.hour_calls[0] < hour_ago:
            self.hour_calls.popleft()
    
    def check_limit(self) -> bool:
        """
        Check if we can make another API call without exceeding limits.
        
        Returns:
            True if under limit, False if limit would be exceeded
        """
        self._clean_old_calls()
        
        minute_count = len(self.minute_calls)
        hour_count = len(self.hour_calls)
        
        if minute_count >= self.max_per_minute:
            logger.warning(
                f"Per-minute rate limit reached: {minute_count}/{self.max_per_minute}"
            )
            return False
        
        if hour_count >= self.max_per_hour:
            logger.warning(
                f"Per-hour rate limit reached: {hour_count}/{self.max_per_hour}"
            )
            return False
        
        return True
    
    def record_call(self):
        """Record an API call for rate limiting"""
        now = datetime.now()
        self.minute_calls.append(now)
        self.hour_calls.append(now)
        
        # Log every 10th call to track usage
        if len(self.hour_calls) % 10 == 0:
            logger.info(
                f"API usage: {len(self.minute_calls)} in last minute, "
                f"{len(self.hour_calls)} in last hour"
            )
    
    def wait_if_needed(self):
        """
        Block and wait if rate limit would be exceeded.
        Returns immediately if under limit.
        """
        self._clean_old_calls()
        
        minute_count = len(self.minute_calls)
        hour_count = len(self.hour_calls)
        
        if minute_count >= self.max_per_minute:
            # Calculate wait time until oldest call expires
            wait_until = self.minute_calls[0] + timedelta(minutes=1)
            wait_seconds = (wait_until - datetime.now()).total_seconds()
            if wait_seconds > 0:
                logger.info(f"Rate limit reached, waiting {wait_seconds:.1f} seconds...")
                time.sleep(wait_seconds + 0.1)  # Small buffer
        
        elif hour_count >= self.max_per_hour:
            wait_until = self.hour_calls[0] + timedelta(hours=1)
            wait_seconds = (wait_until - datetime.now()).total_seconds()
            if wait_seconds > 0:
                logger.info(f"Hourly limit reached, waiting {wait_seconds:.1f} seconds...")
                time.sleep(wait_seconds + 0.1)
    
    def get_stats(self) -> dict:
        """Get current rate limit statistics"""
        self._clean_old_calls()
        return {
            'calls_last_minute': len(self.minute_calls),
            'calls_last_hour': len(self.hour_calls),
            'limit_per_minute': self.max_per_minute,
            'limit_per_hour': self.max_per_hour,
            'remaining_minute': self.max_per_minute - len(self.minute_calls),
            'remaining_hour': self.max_per_hour - len(self.hour_calls)
        }

