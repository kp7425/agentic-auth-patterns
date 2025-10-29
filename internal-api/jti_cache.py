import time
from threading import Lock

class JTICache:
    """In-memory cache for DPoP jti nonces to prevent replay attacks"""

    def __init__(self, max_age=300):
        self.cache = {}  # {jti: timestamp}
        self.max_age = max_age  # 5 minutes
        self.lock = Lock()

    def is_replayed(self, jti):
        """Check if jti has been seen before"""
        with self.lock:
            self._cleanup()
            return jti in self.cache

    def add(self, jti):
        """Add jti to cache"""
        with self.lock:
            self.cache[jti] = time.time()

    def _cleanup(self):
        """Remove expired entries"""
        current_time = time.time()
        expired = [
            jti for jti, timestamp in self.cache.items()
            if current_time - timestamp > self.max_age
        ]
        for jti in expired:
            del self.cache[jti]
