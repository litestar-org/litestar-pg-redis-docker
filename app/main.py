from starlite import LoggingConfig, MediaType, OpenAPIConfig, Provide, Starlite, get
from starlite.plugins.sql_alchemy import SQLAlchemyPlugin

from app.api import v1_router
from app.constants import MESSAGE_HEALTHY
from app.db import close_postgres_connection, create_async_session, get_postgres_connection


@get(path="/health-check", media_type=MediaType.TEXT)
def health_check() -> str:
    return MESSAGE_HEALTHY


logger = LoggingConfig(loggers={"app": {"level": "DEBUG", "handlers": ["console"]}})

app = Starlite(
    route_handlers=[health_check, v1_router],
    plugins=[SQLAlchemyPlugin()],
    on_startup=[logger.configure, get_postgres_connection],
    on_shutdown=[close_postgres_connection],
    openapi_config=OpenAPIConfig(title="Starlite Postgres Example API", version="1.0.0"),
    dependencies={"async_session": Provide(create_async_session)},
)