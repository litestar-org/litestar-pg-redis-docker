from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_200_OK
from starlite import Provide, Router, delete, get, post, put

from app.domain.authors import Author, Repository
from app.lib.service import Service as BaseService
from app.lib.users import User

Service = BaseService[Author]

DETAIL_ROUTE = "/{author_id:uuid}"


def provides_service(db_session: AsyncSession, user: User) -> Service:
    """Constructs repository and service objects for the request."""
    return Service(Repository(session=db_session), user)


@get()
async def get_authors(service: Service) -> list[Author]:
    """Get list of authors."""
    return await service.list()


@post()
async def create_author(data: Author, service: Service) -> Author:
    """Create an `Author`."""
    return await service.create(data)


@get(DETAIL_ROUTE)
async def get_author(service: Service, author_id: UUID) -> Author:
    """Get Author by ID."""
    return await service.get(author_id)


@put(DETAIL_ROUTE)
async def update_author(data: Author, service: Service, author_id: UUID) -> Author:
    """Update an author."""
    return await service.update(author_id, data)


@delete(DETAIL_ROUTE, status_code=HTTP_200_OK)
async def delete_author(service: Service, author_id: UUID) -> Author:
    """Delete Author by ID."""
    return await service.delete(author_id)


router = Router(
    path="/authors",
    route_handlers=[get_authors, create_author, get_author, update_author, delete_author],
    dependencies={"service": Provide(provides_service)},
    tags=["Authors"],
)
