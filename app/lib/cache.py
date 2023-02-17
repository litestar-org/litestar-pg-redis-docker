from typing import TYPE_CHECKING

from starlite import CacheConfig
from starlite.cache.redis_cache_backend import (
    RedisCacheBackend,
    RedisCacheBackendConfig,
)
from starlite.config.cache import default_cache_key_builder

from . import settings

if TYPE_CHECKING:
    from starlite.connection import Request


def cache_key_builder(request: "Request") -> str:
    """App name prefixed cache key builder.

    Parameters
    ----------
    request : Request
        Current request instance.

    Returns
    -------
    str
        App slug prefixed cache key.
    """
    return f"{settings.app.slug}:{default_cache_key_builder(request)}"


redis_backend = RedisCacheBackend(config=RedisCacheBackendConfig(url=settings.redis.URL, port=6379, db=0))
config = CacheConfig(
    backend=redis_backend,  # pyright:ignore[reportGeneralTypeIssues]
    expiration=settings.api.CACHE_EXPIRATION,
    cache_key_builder=cache_key_builder,
)
"""Cache configuration for application."""
