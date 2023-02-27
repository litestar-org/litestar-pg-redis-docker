from starlite.config.cache import CacheConfig
from starlite.storage.redis import RedisStorage

from app.lib import redis

from . import settings

redis_backend = RedisStorage(redis=redis.redis, namespace=settings.app.slug)
config = CacheConfig(backend=redis_backend, expiration=settings.api.CACHE_EXPIRATION)
"""Cache configuration for application."""
