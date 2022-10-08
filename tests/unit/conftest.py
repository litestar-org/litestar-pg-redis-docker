from collections import abc
from typing import Any
from unittest.mock import MagicMock
from uuid import UUID

import pytest

from app.domain import authors
from app.lib import sqlalchemy_plugin, worker

from .utils import GenericMockRepository


@pytest.fixture(scope="session", autouse=True)
def _patch_sqlalchemy_plugin() -> abc.Iterator:
    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr(
        sqlalchemy_plugin.SQLAlchemyConfig,  # type:ignore[attr-defined]
        "on_shutdown",
        MagicMock(),
    )
    yield
    monkeypatch.undo()


@pytest.fixture(scope="session", autouse=True)
def _patch_worker() -> abc.Iterator:
    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr(worker.Worker, "on_app_startup", MagicMock())
    monkeypatch.setattr(worker.Worker, "stop", MagicMock())
    yield
    monkeypatch.undo()


@pytest.fixture(autouse=True)
def _author_repository(raw_authors: list[dict[str, Any]], monkeypatch: pytest.MonkeyPatch) -> None:
    AuthorRepository = GenericMockRepository[authors.Author]
    collection: dict[UUID, authors.Author] = {}
    for raw_author in raw_authors:
        author = authors.Author(**raw_author)
        collection[getattr(author, AuthorRepository.id_attribute)] = author
    monkeypatch.setattr(AuthorRepository, "collection", collection)
    monkeypatch.setattr(authors, "Repository", AuthorRepository)
