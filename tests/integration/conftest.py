# pylint: disable=redefined-outer-name
import asyncio
import timeit
from collections import abc
from pathlib import Path
from typing import TYPE_CHECKING, Any

import asyncpg
import pytest
from pytest_docker.plugin import Services  # type:ignore[import]
from redis.asyncio import Redis
from redis.exceptions import ConnectionError as RedisConnectionError
from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.lib import orm, sqlalchemy_plugin, worker

if TYPE_CHECKING:
    from starlite import Starlite


here = Path(__file__).parent


@pytest.fixture(scope="session")
def event_loop() -> abc.Iterator[asyncio.AbstractEventLoop]:
    """Need the event loop scoped to the session so that we can use it to check
    containers are ready in session scoped containers fixture."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


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


async def redis_responsive(host: str) -> bool:
    """
    Args:
        host: docker IP address.

    Returns:
        Boolean indicating if we can connect to the redis server.
    """
    client: Redis = Redis(host=host, port=6379)
    try:
        return await client.ping()
    except (ConnectionError, RedisConnectionError):
        return False
    finally:
        await client.close()


async def db_responsive(host: str) -> bool:
    """
    Args:
        host: docker IP address.

    Returns:
        Boolean indicating if we can connect to the database.
    """
    try:
        conn = await asyncpg.connect(
            host=host, port=5432, user="postgres", database="postgres", password="super-secret"
        )
    except (ConnectionError, asyncpg.CannotConnectNowError):
        return False
    else:
        try:
            return (await conn.fetchrow("SELECT 1"))[0] == 1  # type:ignore[index,no-any-return]
        finally:
            await conn.close()


@pytest.fixture(scope="session", autouse=True)
async def _containers(docker_ip: str, docker_services: Services) -> None:  # pylint: disable=unused-argument
    """Starts containers for required services, fixture waits until they are
    responsive before returning.

    Args:
        docker_ip:
        docker_services:
    """
    await wait_until_responsive(timeout=30.0, pause=0.1, check=db_responsive, host=docker_ip)
    await wait_until_responsive(timeout=30.0, pause=0.1, check=redis_responsive, host=docker_ip)


@pytest.fixture()
async def redis(docker_ip: str) -> Redis:
    """

    Args:
        docker_ip: IP of docker host.

    Returns:
        Redis client instance, function scoped.
    """
    return Redis(host=docker_ip, port=6379)


@pytest.fixture()
async def engine(docker_ip: str) -> AsyncEngine:
    """Postgresql instance for end-to-end testing.

    Args:
        docker_ip: IP address for TCP connection to Docker containers.

    Returns:
        Async SQLAlchemy engine instance.
    """
    engine = create_async_engine(
        URL(
            drivername="postgresql+asyncpg",
            username="postgres",
            password="super-secret",
            host=docker_ip,
            port=5432,
            database="postgres",
            query={},  # type:ignore[arg-type]
        ),
        echo=False,
        poolclass=NullPool,
    )
    return engine


@pytest.fixture(autouse=True)
async def _seed_db(engine: AsyncEngine, raw_authors: list[dict[str, Any]]) -> abc.AsyncIterator[None]:
    """Populate test database with.

    Args:
        engine: The SQLAlchemy engine instance.
    """
    # get models into metadata
    from app import (  # pylint: disable=[import-outside-toplevel,unused-import] # noqa:F401
        domain,
    )

    metadata = orm.Base.registry.metadata
    author_table = metadata.tables["author"]
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)
    async with engine.begin() as conn:
        await conn.execute(author_table.insert(), raw_authors)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(metadata.drop_all)


@pytest.fixture(autouse=True)
def _patch_db(app: "Starlite", engine: AsyncEngine, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setitem(app.state, sqlalchemy_plugin.config.engine_app_state_key, engine)
    monkeypatch.setitem(
        app.state, sqlalchemy_plugin.config.session_maker_app_state_key, async_sessionmaker(bind=engine)
    )


@pytest.fixture(autouse=True)
def _patch_redis(app: "Starlite", redis: Redis, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(app.cache, "backend", redis)
    monkeypatch.setattr(worker.queue, "redis", redis)
