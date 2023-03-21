from litestar.config.response_cache import ResponseCacheConfig
from litestar.stores.redis import RedisStore

from app.lib.redis import redis

from . import settings

__all__ = ["redis_store_factory"]


def redis_store_factory(name: str) -> RedisStore:
    return RedisStore(redis, namespace=f"{settings.app.slug}:{name}")


config = ResponseCacheConfig(default_expiration=settings.api.CACHE_EXPIRATION)
"""Cache configuration for application."""
