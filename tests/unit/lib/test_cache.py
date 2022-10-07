from app.lib import cache
from app.lib import settings

from starlite.config.cache import default_cache_key_builder
from starlite.testing import RequestFactory

import pytest


def test_cache_key_builder(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings.AppSettings, "slug", "sllluuugg")
    request = RequestFactory().get("/test")
    default_cache_key = default_cache_key_builder(request)
    assert cache.cache_key_builder(request) == f"sllluuugg:{default_cache_key}"
