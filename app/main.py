"""This is the top-level of the application and should only ever import from
other sub-packages of the application, and never be imported from. I.e., never
do `from app.main import whatever` from within any other module of any other
sub-package of the application.

The main point of this restriction is to support unit-testing. We need
to ensure that we can load any other component of the application for
mocking things out in the unittests, without this module being loaded
before that mocking has been completed.

When writing tests, always use the `app` fixture, never import the app
directly from this module.
"""
from typing import Any
from uuid import UUID

import uvicorn
from litestar import Litestar
from litestar.contrib.repository.abc import FilterTypes
from litestar.contrib.repository.exceptions import RepositoryError as RepositoryException
from litestar.contrib.repository.filters import (
    BeforeAfter,
    CollectionFilter,
    LimitOffset,
    OrderBy,
    SearchFilter,
)
from litestar.stores.registry import StoreRegistry
from sqlalchemy.ext.asyncio import AsyncSession

from app.controllers import create_router
from app.lib import (
    cache,
    compression,
    exceptions,
    logging,
    openapi,
    sentry,
    settings,
    sqlalchemy_plugin,
    static_files,
)
from app.lib.dependencies import create_collection_dependencies
from app.lib.health import health_check
from app.lib.redis import redis
from app.lib.service import ServiceError
from app.lib.type_encoders import type_encoders_map

__all__ = ["create_app"]


dependencies = create_collection_dependencies()


def create_app(**kwargs: Any) -> Litestar:
    kwargs.setdefault("debug", settings.app.DEBUG)
    return Litestar(
        response_cache_config=cache.config,
        stores=StoreRegistry(default_factory=cache.redis_store_factory),
        compression_config=compression.config,
        dependencies=dependencies,
        exception_handlers={
            RepositoryException: exceptions.repository_exception_to_http_response,
            ServiceError: exceptions.service_exception_to_http_response,
        },
        logging_config=logging.config,
        openapi_config=openapi.config,
        route_handlers=[health_check, create_router()],
        on_shutdown=[redis.close],
        on_startup=[sentry.configure],
        plugins=[sqlalchemy_plugin.plugin],
        preferred_validation_backend="pydantic",
        signature_namespace={
            "AsyncSession": AsyncSession,
            "FilterTypes": FilterTypes,
            "BeforeAfter": BeforeAfter,
            "CollectionFilter": CollectionFilter,
            "LimitOffset": LimitOffset,
            "UUID": UUID,
            "OrderBy": OrderBy,
            "SearchFilter": SearchFilter,
        },
        static_files_config=[static_files.config],
        type_encoders=type_encoders_map,
        **kwargs,
    )


app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        app,
        host=settings.server.HOST,
        log_level=settings.server.LOG_LEVEL,
        port=settings.server.PORT,
        reload=settings.server.RELOAD,
        timeout_keep_alive=settings.server.KEEPALIVE,
    )
