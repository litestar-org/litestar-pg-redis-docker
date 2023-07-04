# ruff: noqa: B008
from __future__ import annotations

from typing import TYPE_CHECKING

from litestar import Controller, delete, get, post, put
from litestar.di import Provide
from litestar.status_codes import HTTP_200_OK

from app.domain.authors import ReadDTO, Repository, Service, WriteDTO

if TYPE_CHECKING:
    from uuid import UUID

    from litestar.contrib.repository import FilterTypes
    from sqlalchemy.ext.asyncio import AsyncSession

    from app.domain.authors import Author

__all__ = [
    "AuthorController",
]

DETAIL_ROUTE = "/{author_id:uuid}"


def provides_service(db_session: AsyncSession) -> Service:
    """Constructs repository and service objects for the request."""
    return Service(Repository(session=db_session))


class AuthorController(Controller):
    dto = WriteDTO
    return_dto = ReadDTO
    path = "/authors"
    dependencies = {"service": Provide(provides_service, sync_to_thread=False)}
    tags = ["Authors"]

    @get()
    async def get_authors(self, service: Service, filters: list[FilterTypes]) -> list[Author]:
        """Get a list of authors."""
        return await service.list(*filters)

    @post()
    async def create_author(self, data: Author, service: Service) -> Author:
        """Create an `Author`."""
        return await service.create(data)

    @get(DETAIL_ROUTE)
    async def get_author(self, service: Service, author_id: UUID) -> Author:
        """Get Author by ID."""
        return await service.get(author_id)

    @put(DETAIL_ROUTE)
    async def update_author(self, data: Author, service: Service, author_id: UUID) -> Author:
        """Update an author."""
        return await service.update(author_id, data)

    @delete(DETAIL_ROUTE, status_code=HTTP_200_OK)
    async def delete_author(self, service: Service, author_id: UUID) -> Author:
        """Delete Author by ID."""
        return await service.delete(author_id)
