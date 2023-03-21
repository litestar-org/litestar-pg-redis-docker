import pytest
from litestar import Litestar
from litestar.status_codes import HTTP_500_INTERNAL_SERVER_ERROR
from litestar.testing import RequestFactory

from app.lib import exceptions
from app.lib.service import ServiceError


@pytest.mark.parametrize(
    ("exc", "status"),
    [
        (ServiceError, HTTP_500_INTERNAL_SERVER_ERROR),
    ],
)
def test_service_exception_to_http_response(exc: type[ServiceError], status: int) -> None:
    app = Litestar(route_handlers=[])
    request = RequestFactory(app=app, server="testserver").get("/wherever")
    response = exceptions.service_exception_to_http_response(request, exc())
    assert response.status_code == status
