from typing import TYPE_CHECKING

from starlette.status import HTTP_200_OK
from starlite.testing import TestClient

if TYPE_CHECKING:
    from starlite import Starlite


def test_list_authors(app: "Starlite") -> None:
    with TestClient(app=app) as client:
        response = client.get("/authors")
    assert response.status_code == HTTP_200_OK
    assert response.json() == [
        {
            "name": "Agatha Christie",
            "dob": "1890-09-15",
            "id": "97108ac1-ffcb-411d-8b1e-d9183399f63b",
            "created": "0001-01-01T00:00:00",
            "updated": "0001-01-01T00:00:00",
        },
        {
            "name": "Leo Tolstoy",
            "dob": "1828-09-09",
            "id": "5ef29f3c-3560-4d15-ba6b-a2e5c721e4d2",
            "created": "0001-01-01T00:00:00",
            "updated": "0001-01-01T00:00:00",
        },
    ]
