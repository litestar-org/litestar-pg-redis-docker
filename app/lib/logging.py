import logging
import re
from typing import Any

from litestar.logging.config import LoggingConfig
from litestar.status_codes import HTTP_200_OK

from . import settings

__all__ = ["AccessLogFilter"]


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
        return not self.path_filter.match(req_path) or status_code != HTTP_200_OK  # type:ignore[arg-type]


config = LoggingConfig(
    root={"level": settings.app.LOG_LEVEL, "handlers": ["queue_listener"]},
    filters={
        "health_filter": {
            "()": AccessLogFilter,
            "path_re": f"^{settings.api.HEALTH_PATH}$",
        }
    },
    formatters={
        "standard": {
            "format": "%(asctime)s loglevel=%(levelname)-6s logger=%(name)s %(funcName)s() L%(lineno)-4d %(message)s"
        }
    },
    loggers={
        "uvicorn.access": {
            "propagate": False,
            "filters": ["health_filter"],
            "handlers": ["queue_listener"],
        },
        "uvicorn.error": {
            "propagate": False,
            "handlers": ["queue_listener"],
        },
        "saq": {
            "propagate": False,
            "handlers": ["queue_listener"],
        },
        "sqlalchemy.engine": {
            "propagate": False,
            "handlers": ["queue_listener"],
        },
    },
)
"""Pre-configured log config for application."""
