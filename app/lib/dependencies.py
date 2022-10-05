from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from starlite import Parameter, Provide

from . import settings
from .repository.filters import BeforeAfter, CollectionFilter, LimitOffset

if TYPE_CHECKING:
    from starlite import Request
    from starlite_jwt import Token

    from .users import User

DTorNone = datetime | None


async def provide_user(request: "Request[User, Token]") -> "User":
    """Gets the user from the request.

    Args:
        request: current request.

    Returns:
    User | None
    """
    return request.user


def id_filter(ids: list[UUID] = Parameter(query="ids", default=list, required=False)) -> CollectionFilter[UUID]:
    """Return type consumed by ``Repository.filter_in_collection()``.

    Parameters
    ----------
    ids : list[UUID] | None
        Parsed out of comma separated list of values in query params.

    Returns
    -------
    CollectionFilter[UUID]
    """
    return CollectionFilter(field_name="id", values=ids)


def created_filter(
    before: DTorNone = Parameter(query="created-before", default=None, required=False),
    after: DTorNone = Parameter(query="created-after", default=None, required=False),
) -> BeforeAfter:
    """Return type consumed by `Repository.filter_on_datetime_field()`.

    Parameters
    ----------
    before : datetime | None
        Filter for records updated before this date/time.
    after : datetime | None
        Filter for records updated after this date/time.
    """
    return BeforeAfter("created", before, after)


def updated_filter(
    before: DTorNone = Parameter(query="updated-before", default=None, required=False),
    after: DTorNone = Parameter(query="updated-after", default=None, required=False),
) -> BeforeAfter:
    """
    Return type consumed by `Repository.filter_on_datetime_field()`.
    Parameters
    ----------
    before : datetime | None
        Filter for records updated before this date/time.
    after : datetime | None
        Filter for records updated after this date/time.
    """
    return BeforeAfter("updated", before, after)


def limit_offset_pagination(
    page: int = Parameter(ge=1, default=1, required=False),
    page_size: int = Parameter(
        query="page-size",
        ge=1,
        default=settings.api.DEFAULT_PAGINATION_LIMIT,
        required=False,
    ),
) -> LimitOffset:
    """
    Return type consumed by `Repository.apply_limit_offset_pagination()`.
    Parameters
    ----------
    page : int
        LIMIT to apply to select.
    page_size : int
        OFFSET to apply to select.
    """
    return LimitOffset(page_size, page_size * (page - 1))


def create_collection_dependencies() -> dict[str, Provide]:
    """
    Creates a dictionary of provides for pagination endpoints.
    Returns
    -------
    dict[str, Provide]

    """
    return {
        settings.api.LIMIT_OFFSET_DEPENDENCY_KEY: Provide(limit_offset_pagination),
        settings.api.UPDATED_FILTER_DEPENDENCY_KEY: Provide(updated_filter),
        settings.api.CREATED_FILTER_DEPENDENCY_KEY: Provide(created_filter),
        settings.api.ID_FILTER_DEPENDENCY_KEY: Provide(id_filter),
    }
