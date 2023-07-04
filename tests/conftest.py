from datetime import date, datetime
from typing import TYPE_CHECKING, Any
from uuid import UUID

import pytest
from litestar.testing import TestClient

if TYPE_CHECKING:
    from collections import abc

    from litestar import Litestar


@pytest.fixture()
def app() -> "Litestar":
    """Always use this `app` fixture and never do `from app.main import app`
    inside a test module. We need to delay import of the `app.main` module
    until as late as possible to ensure we can mock everything necessary before
    the application instance is constructed.

    Returns:
        The application instance.
    """
    # don't want main imported until everything patched.
    from app.main import create_app

    return create_app(debug=True)


@pytest.fixture()
def client(app: "Litestar") -> "abc.Iterator[TestClient]":
    """Client instance attached to app.

    Args:
        app: The app for testing.

    Returns:
        Test client instance.
    """
    with TestClient(app=app) as c:
        yield c


@pytest.fixture()
def raw_authors() -> list[dict[str, Any]]:
    """Returns:
    Raw set of author data that can either be inserted into tables for integration tests, or
    used to create `Author` instances for unit tests.
    """
    return [
        {
            "id": UUID("97108ac1-ffcb-411d-8b1e-d9183399f63b"),
            "name": "Agatha Christie",
            "dob": date(1890, 9, 15),
            "country_id": UUID("9a225673-202f-4156-8f12-a6e7dd081718"),
            "created": datetime.min,
            "updated": datetime.min,
        },
        {
            "id": UUID("5ef29f3c-3560-4d15-ba6b-a2e5c721e4d2"),
            "name": "Leo Tolstoy",
            "dob": date(1828, 9, 9),
            "country_id": UUID("c0e5b0a1-0b1f-4b0e-8b1a-5e1b0e5e1b0e"),
            "created": datetime.min,
            "updated": datetime.min,
        },
    ]


@pytest.fixture()
def raw_countries() -> list[dict[str, Any]]:
    """Returns:
    Raw set of country data that can either be inserted into tables for integration tests, or
    used to create `Country` instances for unit tests.
    """
    return [
        {
            "id": UUID("9a225673-202f-4156-8f12-a6e7dd081718"),
            "name": "United Kingdom",
            "population": 67000000,
            "created": datetime.min,
            "updated": datetime.min,
        },
        {
            "id": UUID("c0e5b0a1-0b1f-4b0e-8b1a-5e1b0e5e1b0e"),
            "name": "Russia",
            "population": 145000000,
            "created": datetime.min,
            "updated": datetime.min,
        },
        {
            "id": UUID("f0e5b0a1-0b1f-4b0e-8b1a-5e1b0e5e1b0e"),
            "name": "United States",
            "population": 330000000,
            "created": datetime.min,
            "updated": datetime.min,
        },
    ]
