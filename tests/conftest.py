from datetime import date, datetime
from typing import TYPE_CHECKING, Any
from uuid import UUID

import pytest

if TYPE_CHECKING:
    from starlite import Starlite


@pytest.fixture()
def app() -> "Starlite":
    """Always use this `app` fixture and never do `from app.main import app`
    inside a test module. We need to delay import of the `app.main` module
    until as late as possible to ensure we can mock everything necessary before
    the application instance is constructed.

    Returns:
        The application instance.
    """
    # don't want main imported until everything patched.
    from app.main import app as the_app  # pylint: disable=import-outside-toplevel

    return the_app


@pytest.fixture()
def raw_authors() -> list[dict[str, Any]]:
    """

    Returns:
        Raw set of author data that can either be inserted into tables for integration tests, or
        used to create `Author` instances for unit tests.
    """
    return [
        {
            "id": UUID("97108ac1-ffcb-411d-8b1e-d9183399f63b"),
            "name": "Agatha Christie",
            "dob": date(1890, 9, 15),
            "created": datetime.min,
            "updated": datetime.min,
        },
        {
            "id": UUID("5ef29f3c-3560-4d15-ba6b-a2e5c721e4d2"),
            "name": "Leo Tolstoy",
            "dob": date(1828, 9, 9),
            "created": datetime.min,
            "updated": datetime.min,
        },
    ]
