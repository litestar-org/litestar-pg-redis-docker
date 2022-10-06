import asyncio

import uvicorn
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR
from starlite import Provide, Starlite
from starlite.plugins.sql_alchemy import SQLAlchemyPlugin

from app import worker
from app.lib import (
    cache,
    compression,
    exceptions,
    logging,
    openapi,
    response,
    sentry,
    settings,
    sqlalchemy_plugin,
    static_files,
)
from app.lib.auth import jwt_auth
from app.lib.dependencies import create_collection_dependencies, provide_user
from app.lib.health import health_check
from app.lib.redis import redis
from app.lib.users import controllers as user_controllers
from app.lib.worker import Worker, queue

from .controllers import router

dependencies = {settings.api.USER_DEPENDENCY_KEY: Provide(provide_user)}
dependencies.update(create_collection_dependencies())

worker_instance = Worker(queue, worker.functions)


async def worker_on_app_startup() -> None:
    """Attach the worker to the running event loop."""
    loop = asyncio.get_running_loop()
    loop.create_task(worker_instance.start())


app = Starlite(
    cache_config=cache.config,
    compression_config=compression.config,
    dependencies=dependencies,
    exception_handlers={HTTP_500_INTERNAL_SERVER_ERROR: exceptions.logging_exception_handler},
    logging_config=logging.config,
    openapi_config=openapi.config,
    response_class=response.Response,
    route_handlers=[health_check, user_controllers.router, router],
    middleware=[jwt_auth.middleware],
    plugins=[SQLAlchemyPlugin(config=sqlalchemy_plugin.config)],
    on_shutdown=[worker_instance.stop, redis.close],
    on_startup=[sentry.configure, worker_on_app_startup],
    static_files_config=static_files.config,
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
