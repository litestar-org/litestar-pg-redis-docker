import functools
from contextlib import contextmanager
from typing import TYPE_CHECKING, Any, Generic, Optional, TypeVar, overload

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from starlite.exceptions import NotFoundException

from ..db import AsyncScopedSession
from ..model import Base
from .exceptions import RepositoryConflictException, RepositoryException

T = TypeVar("T")
T_row = TypeVar("T_row", bound=tuple[Any, ...])
T_model = TypeVar("T_model", bound=Base)
T_base = TypeVar("T_base", bound=Base)

if TYPE_CHECKING:
    from collections.abc import Mapping
    from uuid import UUID

    from sqlalchemy.engine import Result, ScalarResult
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy.sql import Executable
    from sqlalchemy.sql.selectable import TypedReturnsRows

    from ..types import BeforeAfter, CollectionFilter, LimitOffset


@contextmanager
def catch_sqlalchemy_exception() -> Any:
    """Do something within context to raise a `RepositoryException` chained
    from an original `SQLAlchemyError`.

        >>> try:
        ...     with catch_sqlalchemy_exception():
        ...         raise SQLAlchemyError("Original Exception")
        ... except RepositoryException as exc:
        ...     print(f"caught repository exception from {type(exc.__context__)}")
        ...
        caught repository exception from <class 'sqlalchemy.exc.SQLAlchemyError'>
    """
    try:
        yield
    except IntegrityError as e:
        raise RepositoryConflictException from e
    except SQLAlchemyError as e:
        raise RepositoryException(f"An exception occurred: {e}") from e


class Repository(Generic[T_model]):
    """ABC for resource type Repository objects.

    Subclasses must set the `model_type` class variable.

    Filtering for the route must be done as part of the repository construction. For example, if
    accessing `repository.scalar()` accessor method, and more than one result is returned from the
    query, an exception is raised that will cause a `500` for the client.

    The `scalar()` accessor method is responsible for raising a `NotFoundException`, managing client
    `404` responses for the application.

    Class Attributes
    ----------------
    model : type[T_model]
        A SQLAlchemy declarative class.
    """

    model_type: type[T_model]

    def __init__(  # pylint: disable=too-many-arguments
        self,
        id_: Optional["UUID"] = None,
        id_filter: Optional["CollectionFilter[UUID]"] = None,
        created_filter: Optional["BeforeAfter"] = None,
        updated_filter: Optional["BeforeAfter"] = None,
        limit_offset: Optional["LimitOffset"] = None,
        id_key: str = "id",
    ) -> None:
        self.select = select(self.model_type)
        if id_:
            self.filter_select_by_kwargs(**{id_key: id_})
        if id_filter:
            self.filter_in_collection(id_filter)
        if created_filter:
            self.filter_on_datetime_field(created_filter)
        if updated_filter:
            self.filter_on_datetime_field(updated_filter)
        if limit_offset:
            self.apply_limit_offset_pagination(limit_offset)

    def filter_select_by_kwargs(self, **kwargs: Any) -> None:
        """Add a where clause to `self.select` for each key/value pair in
        `**kwargs` where key is an attribute of `model_type` and value is used
        for an equality test.

        Parameters
        ----------
        kwargs : Any
            Keys should be attributes of `model_type`.
        """
        for k, v in kwargs.items():
            self.select = self.select.where(getattr(self.model_type, k) == v)

    @functools.cached_property
    def session(self) -> "AsyncSession":
        """A scoped session for the repository instance."""
        return AsyncScopedSession()

    @overload
    async def execute(self, statement: "TypedReturnsRows[T_row]", **kwargs: Any) -> "Result[T_row]":
        ...

    @overload
    async def execute(self, statement: "Executable", **kwargs: Any) -> "Result[Any]":
        ...

    async def execute(self, statement: "Executable", **kwargs: Any) -> "Result[Any]":
        """Executes `statement` with error handling.

        Parameters
        ----------
        statement : Executable
            A SQLAlchemy executable.
        kwargs : Any
            Passed as kwargs to `self.session.execute()`.

        Returns
        -------
        sqlalchemy.engine.Result[Any]
        """
        with catch_sqlalchemy_exception():
            return await self.session.execute(statement, **kwargs)

    async def add_flush_refresh(self, instance: T_base) -> T_base:
        """Adds `instance` to `self.session`, flush changes, refresh
        `instance`.

        Parameters
        ----------
        instance : T_base
            A sqlalchemy model.

        Returns
        -------
        T_base
            `instance`
        """
        with catch_sqlalchemy_exception():
            self.session.add(instance)
            await self.session.flush()
            await self.session.refresh(instance)
            return instance

    # create

    def parse_obj(self, data: "Mapping[str, Any]") -> T_model:
        """Creates an instance of `T_model` from `data`.

        Parameters
        ----------
        data : Mapping[str, Any]

        Returns
        -------
        T_model
        """
        return self.model_type(**data)

    async def create(self, data: dict[str, Any]) -> T_model:
        """Create an instance of type `self.model`.

        Notes
        -----
            Does not support converting related entity_mappings into SQLAlchemy instances. This
            could be done in the `data.dict()` method.

        Parameters
        ----------
        data : dict[str, Any]
            Unstructured representation of `T_model`.

        Returns
        -------
        T_model
        """
        return await self.add_flush_refresh(self.parse_obj(data))

    # read

    def apply_limit_offset_pagination(self, data: "LimitOffset") -> None:
        """Paginate the base select query.

        Parameters
        ----------
        data : LimitOffset
        """
        self.select = self.select.limit(data.limit).offset(data.offset)

    def filter_on_datetime_field(self, data: "BeforeAfter") -> None:
        """Add where-clause(s) to the query.

        Parameters
        ----------
        data : BeforeAfter
        """
        field = getattr(self.model_type, data.field_name)
        if data.before is not None:
            self.select = self.select.where(field < data.before)
        if data.after is not None:
            self.select = self.select.where(field > data.before)

    def filter_in_collection(self, data: "CollectionFilter") -> None:
        """Adds a `WHERE ... IN (...)` clause to the query.

        Parameters
        ----------
        data : CollectionFilter
        """
        if data.values is not None:
            self.select = self.select.where(getattr(self.model_type, data.field_name).in_(data.values))

    async def scalars(self, **kwargs: Any) -> "ScalarResult[T_model]":
        """Return the result of `self.select`, filtered by `**kwargs`.

        Parameters
        ----------
        kwargs : Any
            Passed as kwargs to `execute()`.

        Returns
        -------
        ScalarResult
        """
        with catch_sqlalchemy_exception():
            result = await self.execute(self.select, **kwargs)
            # noinspection PyUnresolvedReferences
            return result.scalars()

    @staticmethod
    def check_not_found(instance_or_none: T | None) -> T:
        """Responsible for raising the `404` error to client where we attempt
        to access a `scalar()` query result.

        Parameters
        ----------
        instance_or_none : T | None

        Returns
        -------
        T

        Raises
        ------
        NotFoundException
        """
        if instance_or_none is None:
            raise NotFoundException
        return instance_or_none

    async def scalar(self, **kwargs: Any) -> T_model:
        """Get a scalar result from `self.select`.

        If `self.select` returns more than a single result, a `RepositoryException` is raised.

        Parameters
        ----------
        kwargs : Any
            Passed through to `execute()`.

        Returns
        -------
        T_model
            The type returned by `self.select`

        Raises
        ------
        NotFoundException
            If `self.select` returns no rows.

        RepositoryException
            If `self.select` returns more than a single row.
        """
        with catch_sqlalchemy_exception():
            result = await self.execute(self.select, **kwargs)
            # this will raise for multiple results if the select hasn't been filtered to only return
            # a single result by this point.
            # noinspection PyUnresolvedReferences
            return self.check_not_found(result.scalar_one_or_none())

    # update

    @staticmethod
    def update_model(model: T, data: "Mapping[str, Any]") -> T:
        """Simple helper for setting key/values from `data` as attributes on
        `model`.

        Parameters
        ----------
        model : T_model
            Model instance to be updated
        data : Mapping[str, Any]
            Mapping of data to set as key/value pairs on `model`

        Returns
        -------
        """
        for k, v in data.items():
            setattr(model, k, v)
        return model

    async def update(self, data: "Mapping[str, Any]") -> T_model:
        """Update the model returned from `self.select` with key/val pairs from
        `data`.

        Parameters
        ----------
        data : Mapping[str, Any]
            Key/value pairs used to set attribute vals on result of `self.select`.

        Returns
        -------
        T_model
            The type returned by `self.select`

        Raises
        ------
        NotFoundException
            If `self.select` returns no rows.

        RepositoryException
            If `self.select` returns more than a single row.
        """
        model = await self.scalar()
        return await self.add_flush_refresh(self.update_model(model, data))

    async def upsert(self, data: dict[str, Any]) -> T_model:
        """Update the model returned from `self.select` but if the instance
        doesn't exist create it and populate from ``data``.

        Parameters
        ----------
        data : Mapping[str, Any]
            Key/value pairs used to set attribute vals on result of `self.select`, or new instance
            of `self.model`.

        Returns
        -------
        T_model
            The type returned by `self.select`

        Raises
        ------
        RepositoryException
            If `self.select` returns more than a single row.
        """
        try:
            model = await self.scalar()
        except NotFoundException:
            model = await self.create(data)
        else:
            self.update_model(model, data)
            await self.add_flush_refresh(model)
        return model

    # delete

    async def delete(self) -> T_model:
        """Delete and return the instance returned from `self.scalar()`.

        Returns
        -------
        T_model
            The type returned by `self.select`

        Raises
        ------
        NotFoundException
            If `self.select` returns no rows.

        RepositoryException
            If `self.select` returns more than a single row.
        """
        with catch_sqlalchemy_exception():
            instance = await self.scalar()
            await self.session.delete(instance)
            await self.session.flush()
            return instance
