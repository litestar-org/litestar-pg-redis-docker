import asyncio
import logging
from collections import abc
from functools import partial
from typing import Any

import orjson
import saq  # type:ignore[import]

from .redis import redis

__all__ = [
    "Queue",
    "Worker",
    "WorkerFunction",
    "create_worker_instance",
    "queue",
]

logger = logging.getLogger(__name__)


WorkerFunction = abc.Callable[..., abc.Awaitable[Any]]


class Queue(saq.Queue):  # type:ignore[misc]
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
        kwargs.setdefault("dump", partial(orjson.dumps, default=str))
        kwargs.setdefault("load", orjson.loads)
        super().__init__(*args, **kwargs)


class Worker(saq.Worker):  # type:ignore[misc]
    # same issue: https://github.com/samuelcolvin/arq/issues/182
    SIGNALS: list[str] = []

    async def on_app_startup(self) -> None:
        """Attach the worker to the running event loop."""
        loop = asyncio.get_running_loop()
        loop.create_task(self.start())


queue = Queue(redis)
"""
[Queue][app.lib.worker.Queue] instance instantiated with [redis][app.lib.redis.redis]
instance.
"""


def create_worker_instance(functions: abc.Iterable[WorkerFunction]) -> Worker:
    """

    Args:
        functions: Functions to be called via the async workers.

    Returns:
        The worker instance, instantiated with `functions`.
    """
    return Worker(queue, functions)
