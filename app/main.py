"""This is the top-level of the application and should only ever import from
other sub-packages of the application, and never be imported from. I.e., never
do `from app.main import whatever` from within any other module of any other
sub-package of the application.

The main point of this restriction is to support unit-testing. We need to ensure that we can load
any other component of the application for mocking things out in the unittests, without this module
being loaded before that mocking has been completed.

When writing tests, always use the `app` fixture, never import the app directly from this module.
"""
from uuid import UUID

import uvicorn
from sqlalchemy.ext.asyncio import AsyncSession
from starlite import Starlite
from starlite.contrib.repository.abc import FilterTypes
from starlite.contrib.repository.exceptions import RepositoryError as RepositoryException
from starlite.contrib.repository.filters import BeforeAfter, CollectionFilter, LimitOffset
from starlite.stores.registry import StoreRegistry

from app import worker
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
from app.lib.worker import create_worker_instance

from .controllers import router

dependencies = create_collection_dependencies()
worker_instance = create_worker_instance(worker.functions)


app = Starlite(
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
    route_handlers=[health_check, router],
    on_app_init=[sqlalchemy_plugin.plugin.on_app_init],
    on_shutdown=[worker_instance.stop, redis.close],
    on_startup=[worker_instance.on_app_startup, sentry.configure],
    signature_namespace={
        "AsyncSession": AsyncSession,
        "FilterTypes": FilterTypes,
        "BeforeAfter": BeforeAfter,
        "CollectionFilter": CollectionFilter,
        "LimitOffset": LimitOffset,
        "UUID": UUID,
    },
    static_files_config=[static_files.config],
    type_encoders=type_encoders_map,
)

if __name__ == "__main__":
    uvicorn.run(
        app,
        host=settings.server.HOST,
        log_level=settings.server.LOG_LEVEL,
        port=settings.server.PORT,
        reload=settings.server.RELOAD,
        timeout_keep_alive=settings.server.KEEPALIVE,
    )
