# src/utils/groq_rate_limiter.py

import asyncio
from collections import deque
import time

class GroqRateLimiter:
    """Global rate limiter for Groq API."""
    
    def __init__(self, max_requests_per_minute: int = 30):
        self.max_requests = max_requests_per_minute
        self.requests = deque()
        self._lock = asyncio.Lock()
    
    async def acquire(self):
        """Wait until Groq API quota is available."""
        async with self._lock:
            now = time.time()
            
            # Remove requests older than 60 seconds
            while self.requests and self.requests[0] < now - 60:
                self.requests.popleft()
            
            # If at Groq's limit, wait
            if len(self.requests) >= self.max_requests:
                wait_time = self.requests[0] + 60 - now
                if wait_time > 0:
                    await asyncio.sleep(wait_time)
                    return await self.acquire()
            
            # Track this request
            self.requests.append(now)

# Global Groq rate limiter
GROQ_LIMITER = GroqRateLimiter(max_requests_per_minute=30)