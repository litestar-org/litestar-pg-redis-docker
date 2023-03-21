from typing import TYPE_CHECKING
from unittest.mock import AsyncMock

from litestar.contrib.sqlalchemy.repository import SQLAlchemyAsyncRepository
from litestar.status_codes import HTTP_200_OK, HTTP_503_SERVICE_UNAVAILABLE

from app.lib import settings

if TYPE_CHECKING:
    from litestar.testing import TestClient
    from pytest import MonkeyPatch


def test_health_check(client: "TestClient", monkeypatch: "MonkeyPatch") -> None:
    repo_health_mock = AsyncMock()
    monkeypatch.setattr(SQLAlchemyAsyncRepository, "check_health", repo_health_mock)
    resp = client.get(settings.api.HEALTH_PATH)
    assert resp.status_code == HTTP_200_OK
    assert resp.json() == settings.app.dict()
    repo_health_mock.assert_called_once()


def test_health_check_false_response(client: "TestClient", monkeypatch: "MonkeyPatch") -> None:
    repo_health_mock = AsyncMock(return_value=False)
    monkeypatch.setattr(SQLAlchemyAsyncRepository, "check_health", repo_health_mock)
    resp = client.get(settings.api.HEALTH_PATH)
    assert resp.status_code == HTTP_503_SERVICE_UNAVAILABLE


def test_health_check_exception_raised(client: "TestClient", monkeypatch: "MonkeyPatch") -> None:
    repo_health_mock = AsyncMock(side_effect=ConnectionError)
    monkeypatch.setattr(SQLAlchemyAsyncRepository, "check_health", repo_health_mock)
    resp = client.get(settings.api.HEALTH_PATH)
    assert resp.status_code == HTTP_503_SERVICE_UNAVAILABLE
