from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import ANY

from litestar.status_codes import HTTP_200_OK

if TYPE_CHECKING:
    import pytest
    from httpx import AsyncClient


async def test_list_countries(client: AsyncClient) -> None:
    response = await client.get("/v1/countries")
    assert response.status_code == HTTP_200_OK
    assert response.json() == [
        {
            "created": "0001-01-01T00:00:00",
            "updated": "0001-01-01T00:00:00",
            "id": "9a225673-202f-4156-8f12-a6e7dd081718",
            "name": "United Kingdom",
            "population": 67000000,
        },
        {
            "created": "0001-01-01T00:00:00",
            "updated": "0001-01-01T00:00:00",
            "id": "c0e5b0a1-0b1f-4b0e-8b1a-5e1b0e5e1b0e",
            "name": "Russia",
            "population": 145000000,
        },
        {
            "created": "0001-01-01T00:00:00",
            "id": "f0e5b0a1-0b1f-4b0e-8b1a-5e1b0e5e1b0e",
            "name": "United States",
            "population": 330000000,
            "updated": "0001-01-01T00:00:00",
        },
    ]


async def test_create_country(client: AsyncClient, monkeypatch: pytest.MonkeyPatch) -> None:
    response = await client.post("/v1/countries", json={"name": "Australia", "population": 25000000})
    response_json = response.json()
    assert response_json == {
        "id": ANY,
        "created": ANY,
        "updated": ANY,
        "name": "Australia",
        "population": 25000000,
    }


async def test_get_country(client: AsyncClient) -> None:
    response = await client.get("/v1/countries/9a225673-202f-4156-8f12-a6e7dd081718")
    assert response.json() == {
        "id": "9a225673-202f-4156-8f12-a6e7dd081718",
        "created": "0001-01-01T00:00:00",
        "updated": "0001-01-01T00:00:00",
        "name": "United Kingdom",
        "population": 67000000,
    }


async def test_update_country(client: AsyncClient) -> None:
    response = await client.put(
        "/v1/countries/9a225673-202f-4156-8f12-a6e7dd081718",
        json={
            "id": "9a225673-202f-4156-8f12-a6e7dd081718",
            "created": "0001-01-01T00:00:00",
            "updated": "0001-01-01T00:00:00",
            "name": "United Kingdom",
            "population": 67500000,
        },
    )
    assert response.json() == {
        "id": "9a225673-202f-4156-8f12-a6e7dd081718",
        "created": "0001-01-01T00:00:00",
        "updated": ANY,
        "name": "United Kingdom",
        "population": 67500000,
    }


async def test_delete_country(client: AsyncClient) -> None:
    response = await client.delete("/v1/countries/f0e5b0a1-0b1f-4b0e-8b1a-5e1b0e5e1b0e")
    assert response.status_code == HTTP_200_OK
    assert response.json() == {
        "id": "f0e5b0a1-0b1f-4b0e-8b1a-5e1b0e5e1b0e",
        "name": "United States",
        "population": 330000000,
        "created": "0001-01-01T00:00:00",
        "updated": "0001-01-01T00:00:00",
    }
