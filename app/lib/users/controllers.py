from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from starlite import Provide, Router, delete, get, post, put

from .users import Repository, Service, User

DETAIL_ROUTE = "/{user_id:uuid}"


@get()
async def get_users(service: Service) -> list[User]:
    """Get list of users."""
    return await service.list()


@post()
async def create_user(user: User, service: Service) -> User:
    """Create an `User`."""
    return await service.create(user)


@get(DETAIL_ROUTE)
async def get_user(user_id: UUID, service: Service) -> User:
    """Get User by ID."""
    return await service.get(user_id)


@put(DETAIL_ROUTE)
async def update_user(user_id: UUID, user: User, service: Service) -> User:
    """Update a user."""
    return await service.update(user_id, user)


@delete(DETAIL_ROUTE, status_code=200)
async def delete_user(user_id: UUID, service: Service) -> User:
    """Delete User by ID."""
    return await service.delete(user_id)


def provides_service(db_session: AsyncSession) -> Service:
    """Constructs repository and service objects for the request."""
    return Service(Repository(session=db_session))


router = Router(
    path="/users",
    route_handlers=[get_users, create_user, get_user, update_user, delete_user],
    dependencies={"service": Provide(provides_service)},
    tags=["Users"],
)
