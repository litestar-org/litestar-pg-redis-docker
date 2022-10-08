from typing import TYPE_CHECKING

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlite import get

from app.lib import sqlalchemy_plugin

if TYPE_CHECKING:
    from redis.asyncio import Redis
    from sqlalchemy.ext.asyncio import AsyncEngine
    from starlite import Starlite


def test_cache_on_app(app: "Starlite", redis: "Redis") -> None:
    """Test that the app's cache is patched.

    Args:
        redis: The test Redis client instance.
    """
    assert app.cache.backend is redis


def test_engine_on_app(app: "Starlite", engine: "AsyncEngine") -> None:
    """Test that the app's engine is patched.

    Args:
        engine: The test SQLAlchemy engine instance.
    """
    assert app.state[sqlalchemy_plugin.config.engine_app_state_key] is engine


async def test_db_session_dependency(app: "Starlite", engine: "AsyncEngine") -> None:
    """Test that handlers receive session attached to patched engine.

    Args:
        engine: The patched SQLAlchemy engine instance.
    """

    @get("/db-session-test", opt={"exclude_from_auth": True})
    async def db_session_dependency_patched(db_session: AsyncSession) -> dict[str, str]:
        return {"result": f"{db_session.bind is engine = }"}

    app.register(db_session_dependency_patched)
    # can't use test client as it always starts its own event loop
    # see: https://www.starlette.io/testclient/#asynchronous-tests
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        response = await client.get("/db-session-test")
        assert response.json()["result"] == "db_session.bind is engine = True"
