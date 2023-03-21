from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import ANY

from litestar.status_codes import HTTP_200_OK

if TYPE_CHECKING:
    from httpx import AsyncClient


async def test_list_authors(client: AsyncClient) -> None:
    response = await client.get("/v1/authors")
    assert response.status_code == HTTP_200_OK
    assert response.json() == [
        {
            "created": "0001-01-01T00:00:00",
            "updated": "0001-01-01T00:00:00",
            "id": "97108ac1-ffcb-411d-8b1e-d9183399f63b",
            "name": "Agatha Christie",
            "dob": "1890-09-15",
            "country_id": "9a225673-202f-4156-8f12-a6e7dd081718",
            "nationality": {
                "created": "0001-01-01T00:00:00",
                "updated": "0001-01-01T00:00:00",
                "id": "9a225673-202f-4156-8f12-a6e7dd081718",
                "name": "United Kingdom",
                "population": 67000000,
            },
        },
        {
            "created": "0001-01-01T00:00:00",
            "updated": "0001-01-01T00:00:00",
            "id": "5ef29f3c-3560-4d15-ba6b-a2e5c721e4d2",
            "name": "Leo Tolstoy",
            "dob": "1828-09-09",
            "country_id": "c0e5b0a1-0b1f-4b0e-8b1a-5e1b0e5e1b0e",
            "nationality": {
                "created": "0001-01-01T00:00:00",
                "updated": "0001-01-01T00:00:00",
                "id": "c0e5b0a1-0b1f-4b0e-8b1a-5e1b0e5e1b0e",
                "name": "Russia",
                "population": 145000000,
            },
        },
    ]


async def test_create_author(client: AsyncClient) -> None:
    response = await client.post(
        "/v1/authors", json={"name": "James Patterson", "dob": "1974-03-22", "nationality": None}
    )
    assert response.json() == {
        "id": ANY,
        "created": ANY,
        "updated": ANY,
        "name": "James Patterson",
        "dob": "1974-03-22",
        "country_id": None,
        "nationality": None,
    }


async def test_get_author(client: AsyncClient) -> None:
    response = await client.get("/v1/authors/97108ac1-ffcb-411d-8b1e-d9183399f63b")
    assert response.json() == {
        "id": "97108ac1-ffcb-411d-8b1e-d9183399f63b",
        "created": "0001-01-01T00:00:00",
        "updated": "0001-01-01T00:00:00",
        "name": "Agatha Christie",
        "dob": "1890-09-15",
        "country_id": "9a225673-202f-4156-8f12-a6e7dd081718",
        "nationality": {
            "created": "0001-01-01T00:00:00",
            "updated": "0001-01-01T00:00:00",
            "id": "9a225673-202f-4156-8f12-a6e7dd081718",
            "name": "United Kingdom",
            "population": 67000000,
        },
    }


async def test_update_author(client: AsyncClient) -> None:
    response = await client.put(
        "/v1/authors/97108ac1-ffcb-411d-8b1e-d9183399f63b",
        json={
            "id": "97108ac1-ffcb-411d-8b1e-d9183399f63b",
            "created": "0001-01-01T00:00:00",
            "updated": "0001-01-01T00:00:00",
            "name": "A. Christie",
            "dob": "1890-09-15",
            "country_id": "9a225673-202f-4156-8f12-a6e7dd081718",
        },
    )
    assert response.json() == {
        "id": "97108ac1-ffcb-411d-8b1e-d9183399f63b",
        "created": "0001-01-01T00:00:00",
        "updated": ANY,
        "name": "A. Christie",
        "dob": "1890-09-15",
        "country_id": "9a225673-202f-4156-8f12-a6e7dd081718",
        "nationality": {
            "created": "0001-01-01T00:00:00",
            "updated": "0001-01-01T00:00:00",
            "id": "9a225673-202f-4156-8f12-a6e7dd081718",
            "name": "United Kingdom",
            "population": 67000000,
        },
    }


async def test_delete_author(client: AsyncClient) -> None:
    response = await client.delete("/v1/authors/97108ac1-ffcb-411d-8b1e-d9183399f63b")
    assert response.status_code == HTTP_200_OK
    assert response.json() == {
        "id": "97108ac1-ffcb-411d-8b1e-d9183399f63b",
        "created": "0001-01-01T00:00:00",
        "updated": "0001-01-01T00:00:00",
        "name": "Agatha Christie",
        "dob": "1890-09-15",
        "country_id": "9a225673-202f-4156-8f12-a6e7dd081718",
        "nationality": {
            "created": "0001-01-01T00:00:00",
            "updated": "0001-01-01T00:00:00",
            "id": "9a225673-202f-4156-8f12-a6e7dd081718",
            "name": "United Kingdom",
            "population": 67000000,
        },
    }
