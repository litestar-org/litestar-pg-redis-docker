from starlite import CacheConfig
from starlite.config.cache import default_cache_key_builder
from starlite.connection import Request

from . import settings
from .redis import redis


def cache_key_builder(request: Request) -> str:
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


config = CacheConfig(
    backend=redis,
    expiration=settings.api.CACHE_EXPIRATION,
    cache_key_builder=cache_key_builder,
)
"""Cache configuration for application."""
