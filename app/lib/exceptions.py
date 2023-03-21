import logging
from typing import TYPE_CHECKING

from litestar.contrib.repository.exceptions import (
    ConflictError as RepositoryConflictException,
)
from litestar.contrib.repository.exceptions import (
    NotFoundError as RepositoryNotFoundException,
)
from litestar.contrib.repository.exceptions import (
    RepositoryError as RepositoryException,
)
from litestar.exceptions import (
    HTTPException,
    InternalServerException,
    NotFoundException,
)
from litestar.middleware.exceptions.middleware import create_exception_response

from .service import ServiceError

if TYPE_CHECKING:
    from litestar.connection import Request
    from litestar.response import Response

__all__ = [
    "repository_exception_to_http_response",
    "service_exception_to_http_response",
]

logger = logging.getLogger(__name__)


class ConflictException(HTTPException):
    status_code = 409


def repository_exception_to_http_response(_: "Request", exc: RepositoryException) -> "Response":
    """Transform repository exceptions to HTTP exceptions.

    Args:
        _: The request that experienced the exception.
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
    return create_exception_response(http_exc())


def service_exception_to_http_response(_: "Request", exc: ServiceError) -> "Response":
    """Transform service exceptions to HTTP exceptions.

    Args:
        _: The request that experienced the exception.
        exc: Exception raised during handling of the request.

    Returns:
        Exception response appropriate to the type of original exception.
    """
    return create_exception_response(InternalServerException())
