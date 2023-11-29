from redis.asyncio import Redis

from . import settings

__all__ = ["redis"]

redis = Redis.from_url(str(settings.redis.URL))
"""Async [`Redis`][redis.Redis] instance, configure via."""
