from typing import TYPE_CHECKING
from unittest.mock import MagicMock

import pytest

from app.lib import worker

if TYPE_CHECKING:
    from collections import abc


@pytest.fixture(scope="session", autouse=True)
def _patch_worker() -> "abc.Iterator":
    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr(worker.Worker, "on_app_startup", MagicMock())
    monkeypatch.setattr(worker.Worker, "stop", MagicMock())
    yield
    monkeypatch.undo()
