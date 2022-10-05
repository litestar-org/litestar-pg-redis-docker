from redis.asyncio import Redis

from . import settings

__all__ = ["redis"]

redis = Redis.from_url(settings.redis.URL)
"""
Async [`Redis`][redis.Redis] instance, configure via
[CacheSettings][starlite_saqpg.config.CacheSettings].
"""
