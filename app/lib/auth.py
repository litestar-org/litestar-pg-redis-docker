from typing import TYPE_CHECKING

from starlite_jwt import JWTAuth

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


jwt_auth = JWTAuth(
    retrieve_user_handler=retrieve_user_handler,
    token_secret=settings.api.SECRET_KEY,
    exclude=["/schema", settings.api.HEALTH_PATH],
)
