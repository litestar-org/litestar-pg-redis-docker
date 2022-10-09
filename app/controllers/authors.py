from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_200_OK
from starlite import Provide, Router, delete, get, post, put

from app.domain.authors import Author, ReadDTO, Repository, Service, WriteDTO

DETAIL_ROUTE = "/{author_id:uuid}"


def provides_service(db_session: AsyncSession) -> Service:
    """Constructs repository and service objects for the request."""
    return Service(Repository(session=db_session))


@get()
async def get_authors(service: Service) -> list[ReadDTO]:
    """Get a list of authors."""
    return [ReadDTO.from_orm(item) for item in await service.list()]


@post()
async def create_author(data: WriteDTO, service: Service) -> ReadDTO:
    """Create an `Author`."""
    return ReadDTO.from_orm(await service.create(Author.from_dto(data)))


@get(DETAIL_ROUTE)
async def get_author(service: Service, author_id: UUID) -> ReadDTO:
    """Get Author by ID."""
    return ReadDTO.from_orm(await service.get(author_id))


@put(DETAIL_ROUTE)
async def update_author(data: WriteDTO, service: Service, author_id: UUID) -> ReadDTO:
    """Update an author."""
    return ReadDTO.from_orm(await service.update(author_id, Author.from_dto(data)))


@delete(DETAIL_ROUTE, status_code=HTTP_200_OK)
async def delete_author(service: Service, author_id: UUID) -> ReadDTO:
    """Delete Author by ID."""
    return ReadDTO.from_orm(await service.delete(author_id))


router = Router(
    path="/authors",
    route_handlers=[get_authors, create_author, get_author, update_author, delete_author],
    dependencies={"service": Provide(provides_service)},
    tags=["Authors"],
)
