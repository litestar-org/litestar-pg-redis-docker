from collections import abc
from unittest.mock import MagicMock

import pytest
from starlette.status import (
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
    HTTP_409_CONFLICT,
    HTTP_500_INTERNAL_SERVER_ERROR,
)
from starlite import Starlite, get
from starlite.testing import RequestFactory, create_test_client

from app.lib import exceptions
from app.lib.repository.exceptions import (
    RepositoryConflictException,
    RepositoryException,
    RepositoryNotFoundException,
)
from app.lib.service import ServiceException, UnauthorizedException


def test_after_exception_hook_handler_called(monkeypatch: pytest.MonkeyPatch) -> None:
    logger_mock = MagicMock()
    monkeypatch.setattr(exceptions.logger, "error", logger_mock)

    @get("/error")
    def raises() -> None:
        raise RuntimeError

    with create_test_client(route_handlers=[raises], after_exception=exceptions.after_exception_hook_handler) as client:
        resp = client.get("/error")
        assert resp.status_code == HTTP_500_INTERNAL_SERVER_ERROR

    logger_mock.assert_called_once()


@pytest.mark.parametrize(
    ("exc", "status"),
    [
        (RepositoryConflictException, HTTP_409_CONFLICT),
        (RepositoryNotFoundException, HTTP_404_NOT_FOUND),
        (RepositoryException, HTTP_500_INTERNAL_SERVER_ERROR),
    ],
)
def test_repository_exception_to_http_response(exc: type[RepositoryException], status: int) -> None:
    app = Starlite(route_handlers=[])
    request = RequestFactory(app=app, server="testserver").get("/wherever")
    response = exceptions.repository_exception_to_http_response(request, exc())
    assert response.status_code == status


@pytest.mark.parametrize(
    ("exc", "status"),
    [
        (UnauthorizedException, HTTP_403_FORBIDDEN),
        (ServiceException, HTTP_500_INTERNAL_SERVER_ERROR),
    ],
)
def test_service_exception_to_http_response(exc: type[ServiceException], status: int) -> None:
    app = Starlite(route_handlers=[])
    request = RequestFactory(app=app, server="testserver").get("/wherever")
    response = exceptions.service_exception_to_http_response(request, exc())
    assert response.status_code == status


@pytest.mark.parametrize(
    ("exc", "fn", "expected_message"),
    [
        (
            RepositoryException("message"),
            exceptions.repository_exception_to_http_response,
            b"app.lib.repository.exceptions.RepositoryException: message\n",
        ),
        (
            ServiceException("message"),
            exceptions.service_exception_to_http_response,
            b"app.lib.service.ServiceException: message\n",
        ),
    ],
)
def test_exception_serves_debug_middleware_response(exc: Exception, fn: abc.Callable, expected_message: bytes) -> None:
    app = Starlite(route_handlers=[], debug=True)
    request = RequestFactory(app=app, server="testserver").get("/wherever")
    response = fn(request, exc)
    assert response.body == expected_message
