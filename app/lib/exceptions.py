import logging
from typing import TYPE_CHECKING

from starlite.exceptions import (
    HTTPException,
    InternalServerException,
    NotFoundException,
)
from starlite.middleware.exceptions.debug_response import create_debug_response
from starlite.utils.exception import create_exception_response

from .repository.exceptions import (
    RepositoryConflictException,
    RepositoryException,
    RepositoryNotFoundException,
)
from .service import ServiceException, UnauthorizedException

if TYPE_CHECKING:
    from starlite.connection import Request
    from starlite.datastructures import State
    from starlite.response import Response
    from starlite.types import Scope

__all__ = ["after_exception_hook_handler"]

logger = logging.getLogger(__name__)


class ConflictException(HTTPException):
    status_code = 409


class ForbiddenException(HTTPException):
    status_code = 403


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


def repository_exception_to_http_response(request: "Request", exc: RepositoryException) -> "Response":
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
        return create_debug_response(request, exc)
    return create_exception_response(http_exc())


def service_exception_to_http_response(request: "Request", exc: ServiceException) -> "Response":
    """Transform service exceptions to HTTP exceptions.

    Args:
        request: The request that experienced the exception.
        exc: Exception raised during handling of the request.

    Returns:
        Exception response appropriate to the type of original exception.
    """
    http_exc: type[HTTPException]
    if isinstance(exc, UnauthorizedException):
        http_exc = ForbiddenException
    else:
        http_exc = InternalServerException
    if http_exc is InternalServerException and request.app.debug:
        return create_debug_response(request, exc)
    return create_exception_response(http_exc())
