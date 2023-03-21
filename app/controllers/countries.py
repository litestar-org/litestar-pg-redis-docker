# ruff: noqa: B008
from __future__ import annotations

from typing import TYPE_CHECKING

from litestar import Controller, delete, get, post, put
from litestar.di import Provide
from litestar.params import Dependency
from litestar.status_codes import HTTP_200_OK

from app.domain.countries import ReadDTO, Repository, Service, WriteDTO

if TYPE_CHECKING:
    from uuid import UUID

    from litestar.contrib.repository.abc import FilterTypes
    from sqlalchemy.ext.asyncio import AsyncSession

    from app.domain.countries import Country

__all__ = [
    "CountryController",
]

DETAIL_ROUTE = "/{country_id:uuid}"


def provides_service(db_session: AsyncSession) -> Service:
    """Constructs repository and service objects for the request."""
    return Service(Repository(session=db_session))


class CountryController(Controller):
    dto = WriteDTO
    return_dto = ReadDTO
    path = "/countries"
    dependencies = {"service": Provide(provides_service, sync_to_thread=False)}
    tags = ["Countries"]

    @get()
    async def get_countries(
        self, service: Service, filters: list[FilterTypes] = Dependency(skip_validation=True)
    ) -> list[Country]:
        """Get a list of country."""
        return await service.list(*filters)

    @post()
    async def create_country(self, data: Country, service: Service) -> Country:
        """Create an `Country`."""
        return await service.create(data)

    @get(DETAIL_ROUTE)
    async def get_country(self, service: Service, country_id: UUID) -> Country:
        """Get Country by ID."""
        return await service.get(country_id)

    @put(DETAIL_ROUTE)
    async def update_country(self, data: Country, service: Service, country_id: UUID) -> Country:
        """Update an country."""
        return await service.update(country_id, data)

    @delete(DETAIL_ROUTE, status_code=HTTP_200_OK)
    async def delete_country(self, service: Service, country_id: UUID) -> Country:
        """Delete Country by ID."""
        return await service.delete(country_id)
