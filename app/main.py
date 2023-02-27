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
from __future__ import annotations

import uvicorn
from starlite import Starlite
from starlite.di import Provide
from starlite.plugins.sql_alchemy import SQLAlchemyPlugin

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
from app.lib.dependencies import create_collection_dependencies, provide_user
from app.lib.health import health_check
from app.lib.redis import redis
from app.lib.repository.exceptions import RepositoryException
from app.lib.service import ServiceException
from app.lib.type_encoders import type_encoders_map
from app.lib.worker import create_worker_instance

from .controllers import router

dependencies = {
    settings.api.USER_DEPENDENCY_KEY: Provide(provide_user),
}
dependencies.update(create_collection_dependencies())
worker_instance = create_worker_instance(worker.functions)


app = Starlite(
    after_exception=[exceptions.after_exception_hook_handler],
    cache_config=cache.config,
    compression_config=compression.config,
    dependencies=dependencies,
    exception_handlers={
        RepositoryException: exceptions.repository_exception_to_http_response,
        ServiceException: exceptions.service_exception_to_http_response,
    },
    logging_config=logging.config,
    openapi_config=openapi.config,
    route_handlers=[health_check, router],
    plugins=[SQLAlchemyPlugin(config=sqlalchemy_plugin.config)],
    on_shutdown=[worker_instance.stop, redis.close],
    on_startup=[worker_instance.on_app_startup, sentry.configure],
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
