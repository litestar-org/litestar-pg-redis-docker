from typing import TYPE_CHECKING
from uuid import uuid4

from starlite import Response, get
from starlite.contrib.jwt import JWTAuth

from . import settings
from .users import User

if TYPE_CHECKING:
    from starlite import ASGIConnection


default_user = User(name=settings.api.DEFAULT_USER_NAME)


async def retrieve_user_handler(
    id_: str, connection: "ASGIConnection"  # pylint: disable=[unused-argument]
) -> User | None:
    """Get the user for the request.

    Args:
        id_: The ID of the user.
        connection: The client connection.

    Returns:
        The user for the connection if one exists with given `id_`.
    """
    return default_user


# Given an instance of 'JWTAuth' we can create a login handler function:
@get("/login")
def login_handler() -> Response[User]:
    """__todo__"""
    # we have a user instance - probably by retrieving it from persistence using another lib.
    # what's important for our purposes is to have an identifier:
    user = User(name="Moishe Zuchmir", email="zuchmir@moishe.com", id=uuid4())

    return jwt_auth.login(identifier=str(user.id), response_body=user)


jwt_auth = JWTAuth(
    retrieve_user_handler=retrieve_user_handler,
    token_secret=settings.api.SECRET_KEY,
    exclude=["/schema", settings.api.HEALTH_PATH],
)
