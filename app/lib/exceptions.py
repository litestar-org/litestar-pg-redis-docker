import logging
from typing import TYPE_CHECKING

from starlette.middleware.errors import ServerErrorMiddleware
from starlette.responses import Response
from starlite.connection import Request
from starlite.exceptions import (
    HTTPException,
    InternalServerException,
    NotFoundException,
)
from starlite.utils.exception import create_exception_response

from .repository.exceptions import (
    RepositoryConflictException,
    RepositoryException,
    RepositoryNotFoundException,
)

if TYPE_CHECKING:
    from starlite.datastructures import State
    from starlite.types import Scope

__all__ = ["after_exception_hook_handler"]

logger = logging.getLogger(__name__)


class ConflictException(HTTPException):
    status_code = 409


def after_exception_hook_handler(exc: Exception, scope: "Scope", state: "State") -> None:
    """Logs exception and returns appropriate response.

    Args:
        exc: the exception that was raised.
        scope: scope of the request
        state: application state
    """
    logger.error(
        "Application Exception\n\nRequest Scope: %s\n\nApplication State: %s\n\n",
        scope,
        state.dict(),
        exc_info=exc,
    )


def repository_exception_to_http_response(request: Request, exc: RepositoryException) -> Response:
    """Transform repository exceptions to HTTP exceptions.

    Args:
        request: The request that experienced the exception.
        exc: Exception raised during handling of the request.

    Returns:
        Exception response appropriate to the type of original exception.
    """
    http_exc: type[HTTPException]
    if isinstance(exc, RepositoryNotFoundException):
        http_exc = NotFoundException
    elif isinstance(exc, RepositoryConflictException):
        http_exc = ConflictException
    else:
        http_exc = InternalServerException

    if http_exc is InternalServerException and request.app.debug:
        # use the server error middleware to create an HTML formatted response for us
        server_middleware = ServerErrorMiddleware(app=request.app)  # type: ignore[arg-type]
        return server_middleware.debug_response(request=request, exc=exc)  # type: ignore[arg-type]
    return create_exception_response(http_exc())
