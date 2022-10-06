from typing import TYPE_CHECKING

from sqlalchemy.ext.asyncio import AsyncSession
from starlite import get
from starlite.testing import TestClient

from app.lib import sqlalchemy_plugin
from app.main import app

if TYPE_CHECKING:
    from redis.asyncio import Redis
    from sqlalchemy.ext.asyncio import AsyncEngine


def test_engine_on_app(engine: "AsyncEngine") -> None:
    """Test that the app's engine is patched.

    Args:
        engine: The test SQLAlchemy engine instance.
    """
    assert app.state[sqlalchemy_plugin.config.engine_app_state_key] is engine


def test_cache_on_app(redis: "Redis") -> None:
    """Test that the app's cache is patched.

    Args:
        redis: The test Redis client instance.
    """
    assert app.cache.backend is redis


def test_db_session_dependency(engine: "AsyncEngine") -> None:
    """Test that handlers receive session attached to patched engine.

    Args:
        engine: The patched SQLAlchemy engine instance.
        monkeypatch: _
    """

    @get("/db-session-test", opt={"exclude_from_auth": True})
    async def db_session_dependency_patched(db_session: AsyncSession) -> dict[str, str]:
        return {"result": f"{db_session.bind is engine = }"}

    app.register(db_session_dependency_patched)
    with TestClient(app) as client:
        response = client.get("/db-session-test")
        assert response.json()["result"] == "db_session.bind is engine = True"
