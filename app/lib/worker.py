from __future__ import annotations

import asyncio
from collections import abc
from functools import partial
from typing import TYPE_CHECKING, Any

import msgspec
import saq
from starlite.utils.serialization import default_serializer

from . import settings, type_encoders
from .redis import redis

if TYPE_CHECKING:
    from collections.abc import Collection
    from signal import Signals

__all__ = [
    "Queue",
    "Worker",
    "WorkerFunction",
    "create_worker_instance",
    "queue",
]

WorkerFunction = abc.Callable[..., abc.Awaitable[Any]]

encoder = msgspec.json.Encoder(enc_hook=partial(default_serializer, type_encoders=type_encoders.type_encoders_map))
decoder = msgspec.json.Decoder()


class Queue(saq.Queue):
    """[SAQ Queue](https://github.com/tobymao/saq/blob/master/saq/queue.py)

    Configures `orjson` for JSON serialization/deserialization if not otherwise configured.

    Parameters
    ----------
    *args : Any
        Passed through to `saq.Queue.__init__()`
    **kwargs : Any
        Passed through to `saq.Queue.__init__()`
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        kwargs.setdefault("dump", encoder.encode)
        kwargs.setdefault("load", decoder.decode)
        kwargs.setdefault("name", "background-worker")
        super().__init__(*args, **kwargs)

    def namespace(self, key: str) -> str:
        """Make the namespace unique per app."""
        return f"{settings.app.slug}:{self.name}:{key}"


class Worker(saq.Worker):
    # same issue: https://github.com/samuelcolvin/arq/issues/182
    SIGNALS: list[Signals] = []

    async def on_app_startup(self) -> None:
        """Attach the worker to the running event loop."""
        loop = asyncio.get_running_loop()
        loop.create_task(self.start())


queue = Queue(redis)
"""[Queue][app.lib.worker.Queue] instance instantiated with.

[redis][app.lib.redis.redis] instance.
"""


def create_worker_instance(functions: Collection[WorkerFunction]) -> Worker:
    """

    Args:
        functions: Functions to be called via the async workers.

    Returns:
        The worker instance, instantiated with `functions`.
    """
    return Worker(queue, functions)
