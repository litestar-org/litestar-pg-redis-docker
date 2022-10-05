import logging

from starlette.responses import Response
from starlite.connection import Request
from starlite.utils.exception import create_exception_response

__all__ = ["logging_exception_handler"]

logger = logging.getLogger(__name__)


def logging_exception_handler(_: Request, exc: Exception) -> Response:
    """Logs exception and returns appropriate response.

    Parameters
    ----------
    _ : Request
        The request that caused the exception.
    exc :
        The exception caught by the Starlite exception handling middleware and passed to the
        callback.

    Returns
    -------
    Response
    """
    logger.error("Application Exception", exc_info=exc)
    return create_exception_response(exc)
