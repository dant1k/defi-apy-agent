"""Cache decorators for API endpoints"""
from functools import wraps
from typing import Callable, Any
from app.core.cache import cache_service
from app.core.config import settings


def cache_response(ttl: int = 300, key_prefix: str = "api"):
    """Decorator to cache function results"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Build cache key
            cache_key = cache_service._make_key(key_prefix, *args, **kwargs)
            
            # Try to get from cache
            cached = await cache_service.get(cache_key)
            if cached is not None:
                return cached
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Cache result
            if result is not None:
                await cache_service.set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator


def cache_dexes(ttl: int = None):
    """Cache decorator for /dexes endpoint"""
    if ttl is None:
        ttl = settings.CACHE_DEXES_TTL
    return cache_response(ttl=ttl, key_prefix="dexes")


def cache_dex_detail(ttl: int = None):
    """Cache decorator for /dexes/{slug} endpoint"""
    if ttl is None:
        ttl = settings.CACHE_DEX_DETAIL_TTL
    return cache_response(ttl=ttl, key_prefix="dex")


def cache_pools(ttl: int = None):
    """Cache decorator for /dexes/{slug}/pools endpoint"""
    if ttl is None:
        ttl = settings.CACHE_POOLS_TTL
    return cache_response(ttl=ttl, key_prefix="pools")

