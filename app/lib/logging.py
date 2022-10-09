import logging
import re
from typing import Any

from starlette.status import HTTP_200_OK
from starlite import LoggingConfig

from . import settings


class AccessLogFilter(logging.Filter):
    """Filter for omitting log records from uvicorn access logs based on
    request path.

    Parameters
    ----------
    *args : Any
        Unpacked into [`logging.Filter.__init__()`][logging.Filter].
    path_re : str
        Regex, paths matched are filtered.
    **kwargs : Any
        Unpacked into [`logging.Filter.__init__()`][logging.Filter].
    """

    def __init__(self, *args: Any, path_re: str, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.path_filter = re.compile(path_re)

    def filter(self, record: logging.LogRecord) -> bool:
        *_, req_path, _, status_code = record.args  # type:ignore[misc]
        if (
            self.path_filter.match(req_path)  # type:ignore[arg-type]
            and status_code == HTTP_200_OK
        ):
            return False
        return True


config = LoggingConfig(
    root={"level": settings.app.LOG_LEVEL, "handlers": ["queue_listener"]},
    filters={
        "health_filter": {
            "()": AccessLogFilter,
            "path_re": f"^{settings.api.HEALTH_PATH}$",
        }
    },
    formatters={"standard": {"format": "%(levelname)s - %(asctime)s - %(name)s - %(funcName)s - %(message)s"}},
    loggers={
        "app": {
            "propagate": True,
        },
        "uvicorn.access": {
            "propagate": True,
            "filters": ["health_filter"],
        },
        "uvicorn.error": {
            "propagate": True,
        },
        "sqlalchemy.engine": {
            "propagate": True,
        },
    },
)
"""Pre-configured log config for application."""
