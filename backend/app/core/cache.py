"""Redis cache utilities"""
import json
import hashlib
from typing import Optional, Any
import redis.asyncio as redis
from app.core.config import settings


class CacheService:
    """Redis cache service"""
    
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
    
    async def connect(self):
        """Connect to Redis"""
        if self.redis_client is None:
            self.redis_client = await redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )
    
    async def close(self):
        """Close Redis connection"""
        if self.redis_client:
            await self.redis_client.aclose()
            self.redis_client = None
    
    def _make_key(self, prefix: str, *args, **kwargs) -> str:
        """Create cache key from prefix and parameters"""
        key_parts = [prefix]
        
        # Add positional args
        for arg in args:
            if arg is not None:
                key_parts.append(str(arg))
        
        # Add keyword args (sorted for consistency)
        if kwargs:
            sorted_kwargs = sorted(kwargs.items())
            for k, v in sorted_kwargs:
                if v is not None:
                    key_parts.append(f"{k}:{v}")
        
        key = ":".join(key_parts)
        # Hash if key is too long
        if len(key) > 250:
            key_hash = hashlib.md5(key.encode()).hexdigest()
            return f"{prefix}:hash:{key_hash}"
        return key
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.redis_client:
            await self.connect()
        
        try:
            value = await self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            print(f"Cache get error: {e}")
            return None
    
    async def set(
        self, 
        key: str, 
        value: Any, 
        ttl: int = 300
    ) -> bool:
        """Set value in cache with TTL"""
        if not self.redis_client:
            await self.connect()
        
        try:
            serialized = json.dumps(value, default=str)
            await self.redis_client.setex(key, ttl, serialized)
            return True
        except Exception as e:
            print(f"Cache set error: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if not self.redis_client:
            await self.connect()
        
        try:
            await self.redis_client.delete(key)
            return True
        except Exception as e:
            print(f"Cache delete error: {e}")
            return False
    
    async def get_or_set(
        self,
        key: str,
        fetch_func,
        ttl: int = 300,
        *args,
        **kwargs
    ) -> Any:
        """Get from cache or fetch and cache"""
        # Try to get from cache
        cached = await self.get(key)
        if cached is not None:
            return cached
        
        # Fetch fresh data
        value = await fetch_func(*args, **kwargs)
        
        # Cache it
        if value is not None:
            await self.set(key, value, ttl)
        
        return value


# Global cache instance
cache_service = CacheService()

