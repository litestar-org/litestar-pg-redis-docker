from __future__ import annotations

import asyncio
import timeit
from pathlib import Path
from typing import TYPE_CHECKING

import asyncpg
import pytest
from httpx import AsyncClient
from litestar.contrib.sqlalchemy.base import UUIDBase
from redis.asyncio import Redis
from redis.exceptions import ConnectionError as RedisConnectionError
from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.lib import sqlalchemy_plugin, worker

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Awaitable, Callable, Iterator
    from typing import Any

    from litestar import Litestar
    from pytest_docker.plugin import Services


here = Path(__file__).parent


@pytest.fixture(scope="session")
def event_loop() -> Iterator[asyncio.AbstractEventLoop]:
    """Need the event loop scoped to the session so that we can use it to check
    containers are ready in session scoped containers fixture.
    """
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def docker_compose_file() -> Path:
    """Returns:
    Path to the docker-compose file for end-to-end test environment.
    """
    return here / "docker-compose.yml"


async def wait_until_responsive(check: Callable[..., Awaitable], timeout: float, pause: float, **kwargs: Any) -> None:
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

    raise ConnectionError("Timeout reached while waiting on service!")


async def redis_responsive(host: str) -> bool:
    """Args:
        host: docker IP address.

    Returns:
        Boolean indicating if we can connect to the redis server.
    """
    client: Redis = Redis(host=host, port=6397)
    try:
        return await client.ping()
    except (ConnectionError, RedisConnectionError):
        return False
    finally:
        await client.close()


async def db_responsive(host: str) -> bool:
    """Args:
        host: docker IP address.

    Returns:
        Boolean indicating if we can connect to the database.
    """
    try:
        conn = await asyncpg.connect(
            host=host, port=5423, user="postgres", database="postgres", password="super-secret"  # noqa: S106
        )
    except (ConnectionError, asyncpg.CannotConnectNowError):
        return False

    try:
        return (await conn.fetchrow("SELECT 1"))[0] == 1  # type:ignore[index,no-any-return]
    finally:
        await conn.close()


@pytest.fixture(scope="session", autouse=True)
async def _containers(docker_ip: str, docker_services: Services) -> None:
    """Starts containers for required services, fixture waits until they are
    responsive before returning.
    """
    await wait_until_responsive(timeout=30.0, pause=0.1, check=db_responsive, host=docker_ip)
    await wait_until_responsive(timeout=30.0, pause=0.1, check=redis_responsive, host=docker_ip)


@pytest.fixture()
async def redis(docker_ip: str) -> Redis:
    """Args:
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
    return create_async_engine(
        URL(
            drivername="postgresql+asyncpg",
            username="postgres",
            password="super-secret",  # noqa: S106
            host=docker_ip,
            port=5423,
            database="postgres",
            query={},  # type:ignore[arg-type]
        ),
        echo=False,
        poolclass=NullPool,
    )


@pytest.fixture(autouse=True)
async def _seed_db(
    engine: AsyncEngine, raw_countries: list[dict[str, Any]], raw_authors: list[dict[str, Any]]
) -> AsyncIterator[None]:
    """Populate test database."""
    # get models into metadata

    metadata = UUIDBase.registry.metadata
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)

    country_table = metadata.tables["country"]
    async with engine.begin() as conn:
        await conn.execute(country_table.insert(), raw_countries)

    author_table = metadata.tables["author"]
    async with engine.begin() as conn:
        await conn.execute(author_table.insert(), raw_authors)

    yield

    async with engine.begin() as conn:
        await conn.run_sync(metadata.drop_all)


@pytest.fixture(autouse=True)
def _patch_db(app: Litestar, engine: AsyncEngine, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setitem(app.state, sqlalchemy_plugin.config.engine_app_state_key, engine)
    monkeypatch.setitem(
        app.state, sqlalchemy_plugin.config.session_maker_app_state_key, async_sessionmaker(bind=engine)
    )


@pytest.fixture(autouse=True)
def _patch_redis(app: Litestar, redis: Redis, monkeypatch: pytest.MonkeyPatch) -> None:
    cache_config = app.response_cache_config
    assert cache_config is not None
    monkeypatch.setattr(app.stores.get(cache_config.store), "_redis", redis)
    monkeypatch.setattr(worker.queue, "redis", redis)


@pytest.fixture(name="client")
async def fx_client(app: Litestar) -> AsyncIterator[AsyncClient]:
    """Async client that calls requests on the app.

    We need to use `httpx.AsyncClient` here, as `litestar.TestClient` creates its own event loop to
    run async calls to the underlying app in a sync context, resulting in errors like:

    ```text
    ValueError: The future belongs to a different loop than the one specified as the loop argument
    ```

    Related: https://www.starlette.io/testclient/#asynchronous-tests

    The httpx async client will call the app, but not trigger lifecycle events. However, we need
    the lifecycle events to be called to configure the logging, hence `LifespanManager`.
    """
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        yield client
