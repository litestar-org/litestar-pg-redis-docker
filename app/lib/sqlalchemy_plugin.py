from functools import partial
from typing import TYPE_CHECKING, Any, cast
from uuid import UUID

from orjson import dumps, loads
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool
from starlite.plugins.sql_alchemy import SQLAlchemyConfig as _SQLAlchemyConfig
from starlite.plugins.sql_alchemy.config import (
    SESSION_SCOPE_KEY,
    SESSION_TERMINUS_ASGI_EVENTS,
)

from . import settings

if TYPE_CHECKING:
    from starlite.datastructures.state import State
    from starlite.types import Message, Scope

__all__ = [
    "engine",
    "async_session_factory",
]


def _default(val: Any) -> str:
    if isinstance(val, UUID):
        return str(val)
    raise TypeError()


engine = create_async_engine(
    settings.db.URL,
    echo=settings.db.ECHO,
    echo_pool=settings.db.ECHO_POOL,
    json_serializer=partial(dumps, default=_default),
    max_overflow=settings.db.POOL_MAX_OVERFLOW,
    pool_size=settings.db.POOL_SIZE,
    pool_timeout=settings.db.POOL_TIMEOUT,
    poolclass=NullPool if settings.db.POOL_DISABLE else None,
)
"""Configure via [DatabaseSettings][starlite_saqpg.settings.DatabaseSettings]. Overrides default JSON
serializer to use `orjson`. See [`create_async_engine()`][sqlalchemy.ext.asyncio.create_async_engine]
for detailed instructions.
"""
async_session_factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
"""
Database session factory. See [`async_sessionmaker()`][sqlalchemy.ext.asyncio.async_sessionmaker].
"""


@event.listens_for(engine.sync_engine, "connect")
def _sqla_on_connect(dbapi_connection: Any, _: Any) -> Any:
    """Using orjson for serialization of the json column values means that the
    output is binary, not `str` like `json.dumps` would output.

    SQLAlchemy expects that the json serializer returns `str` and calls `.encode()` on the value to
    turn it to bytes before writing to the JSONB column. I'd need to either wrap `orjson.dumps` to
    return a `str` so that SQLAlchemy could then convert it to binary, or do the following, which
    changes the behaviour of the dialect to expect a binary value from the serializer.

    See Also https://github.com/sqlalchemy/sqlalchemy/blob/14bfbadfdf9260a1c40f63b31641b27fe9de12a0/lib/sqlalchemy/dialects/postgresql/asyncpg.py#L934
    """

    def encoder(bin_value: bytes) -> bytes:
        # \x01 is the prefix for jsonb used by PostgreSQL.
        # asyncpg requires it when format='binary'
        return b"\x01" + bin_value

    def decoder(bin_value: bytes) -> Any:
        # the byte is the \x01 prefix for jsonb used by PostgreSQL.
        # asyncpg returns it when format='binary'
        return loads(bin_value[1:])

    dbapi_connection.await_(
        dbapi_connection.driver_connection.set_type_codec(
            "jsonb",
            encoder=encoder,
            decoder=decoder,
            schema="pg_catalog",
            format="binary",
        )
    )


class SQLAlchemyConfig(_SQLAlchemyConfig):
    @staticmethod
    async def before_send_handler(message: "Message", _: "State", scope: "Scope") -> None:
        session = cast(AsyncSession | None, scope.get(SESSION_SCOPE_KEY))
        try:
            if session is not None and message["type"] == "http.response.start":
                if 200 <= message["status"] < 300:
                    await session.commit()
                else:
                    await session.rollback()
        finally:
            if session is not None and message["type"] in SESSION_TERMINUS_ASGI_EVENTS:
                await session.close()
                del scope[SESSION_SCOPE_KEY]  # type:ignore[misc]

    def update_app_state(self, state: "State") -> None:
        state[self.engine_app_state_key] = engine
        state[self.session_maker_app_state_key] = async_session_factory


config = SQLAlchemyConfig(
    connection_string=settings.db.URL,
    dependency_key=settings.api.DB_SESSION_DEPENDENCY_KEY,
)
