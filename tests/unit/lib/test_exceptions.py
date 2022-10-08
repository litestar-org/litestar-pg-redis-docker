from unittest.mock import MagicMock

import pytest
from starlette.status import (
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


def test_repository_exception_serves_debug_middleware_response() -> None:
    app = Starlite(route_handlers=[], debug=True)
    request = RequestFactory(app=app, server="testserver").get("/wherever")
    response = exceptions.repository_exception_to_http_response(request, RepositoryException("message"))
    assert response.body == b"app.lib.repository.exceptions.RepositoryException: message\n"
