# pylint: disable=redefined-outer-name
import asyncio
import timeit
from collections import abc
from datetime import date
from pathlib import Path
from typing import Any

import asyncpg
import pytest
from pytest_docker.plugin import Services
from redis.asyncio import Redis
from redis.exceptions import ConnectionError as RedisConnectionError
from sqlalchemy import text
from sqlalchemy.engine import URL
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app import lib
from app.main import app, worker_instance

here = Path(__file__).parent


@pytest.fixture(scope="session")
def docker_compose_file() -> Path:
    """
    Returns:
        Path to the docker-compose file for end-to-end test environment.
    """
    return here / "docker-compose.yml"


async def wait_until_responsive(
    check: abc.Callable[..., abc.Awaitable], timeout: float, pause: float, **kwargs: Any
) -> None:
    """Wait until a service is responsive.

    Args:
        check: Coroutine, return truthy value when waiting should stop.
        timeout: Maximum seconds to wait.
        pause: Seconds to wait between calls to `check`.
        **kwargs: Given as kwargs to `check`.
    """
    ref = timeit.default_timer()
    now = ref
    while (now - ref) < timeout:
        if await check(**kwargs):
            return
        await asyncio.sleep(pause)
        now = timeit.default_timer()

    raise Exception("Timeout reached while waiting on service!")


async def redis_responsive(redis: Redis) -> bool:
    """
    Args:
        redis: Redis client instance.

    Returns:
        Boolean indicating if we can connect to the redis server.
    """
    try:
        return await redis.ping()
    except RedisConnectionError:
        return False


@pytest.fixture()
async def redis(docker_ip: str, docker_services: Services) -> Redis:
    """Redis instance for end-to-end testing.

    Args:
        docker_ip: IP address for TCP connection to Docker containers.
        docker_services: Fixture that starts and stops services.

    Returns:
        Async redis client instance.
    """
    port = docker_services.port_for("redis", 6379)
    redis: Redis = Redis(host=docker_ip, port=port)
    await wait_until_responsive(timeout=30.0, pause=0.1, check=redis_responsive, redis=redis)
    return redis


async def db_responsive(engine: AsyncEngine) -> bool:
    """
    Args:
        engine: SQLAlchemy async engine instance.

    Returns:
        Boolean indicating if we can connect to the database.
    """
    try:
        async with engine.begin() as connection:
            try:
                return (await connection.execute(text("SELECT 1"))).scalar() == 1
            except DBAPIError:
                return False
    except (ConnectionError, asyncpg.CannotConnectNowError):
        return False


@pytest.fixture()
async def engine(docker_ip: str, docker_services: Services) -> AsyncEngine:
    """Postgresql instance for end-to-end testing.

    Args:
        docker_ip: IP address for TCP connection to Docker containers.
        docker_services: Fixture that starts and stops services.

    Returns:
        Async SQLAlchemy engine instance.
    """
    port = docker_services.port_for("postgres", 5432)
    engine = create_async_engine(
        URL(
            drivername="postgresql+asyncpg",
            username="postgres",
            password="super-secret",
            host=docker_ip,
            port=port,
            database="postgres",
            query={},  # type:ignore[arg-type]
        ),
        echo=False,
        poolclass=NullPool,
    )
    await wait_until_responsive(timeout=30.0, pause=0.1, check=db_responsive, engine=engine)
    return engine


@pytest.fixture(autouse=True)
async def _seed_db(engine: AsyncEngine) -> abc.AsyncIterator[None]:
    """Populate test database with.

    Args:
        engine: The SQLAlchemy engine instance.
    """
    metadata = lib.orm.Base.registry.metadata
    author_table = metadata.tables["author"]
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)
    async with engine.begin() as conn:
        await conn.execute(
            author_table.insert(),
            [
                {"name": "Agatha Christie", "dob": date(1890, 9, 15)},
                {"name": "Leo Tolstoy", "dob": date(1828, 9, 9)},
            ],
        )
    yield
    async with engine.begin() as conn:
        await conn.run_sync(metadata.drop_all)


@pytest.fixture(autouse=True)
def _patch_db(engine: AsyncEngine, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(lib.sqlalchemy_plugin, "engine", engine)
    monkeypatch.setitem(app.state, lib.sqlalchemy_plugin.config.engine_app_state_key, engine)
    monkeypatch.setitem(app.state, lib.sqlalchemy_plugin.config.session_maker_app_state_key, async_sessionmaker(engine))


@pytest.fixture(autouse=True)
def _patch_redis(redis: Redis, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(lib.redis, "redis", redis)
    monkeypatch.setattr(app.cache, "backend", redis)
    monkeypatch.setattr(worker_instance.queue, "redis", redis)
