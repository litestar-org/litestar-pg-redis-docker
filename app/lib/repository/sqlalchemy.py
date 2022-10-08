from collections import abc
from contextlib import contextmanager
from typing import TYPE_CHECKING, Any, Literal, TypeVar

from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from .abc import AbstractRepository
from .exceptions import RepositoryConflictException, RepositoryException
from .filters import BeforeAfter, CollectionFilter, LimitOffset

if TYPE_CHECKING:
    from datetime import datetime

    from sqlalchemy import Select
    from sqlalchemy.ext.asyncio import AsyncSession

    from .. import orm
    from .types import FilterTypes

__all__ = [
    "SQLAlchemyRepository",
    "T_model",
]

T = TypeVar("T")
T_model = TypeVar("T_model", bound="orm.Base")


@contextmanager
def wrap_sqlalchemy_exception() -> Any:
    """Do something within context to raise a `RepositoryException` chained
    from an original `SQLAlchemyError`.

        >>> try:
        ...     with wrap_sqlalchemy_exception():
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


class SQLAlchemyRepository(AbstractRepository[T_model]):
    model_type: type[T_model]

    def __init__(self, session: "AsyncSession", select_: "Select[tuple[T_model]] | None" = None) -> None:
        self._session = session
        self._select = select(self.model_type) if select_ is None else select_

    async def add(self, data: T_model) -> T_model:
        with wrap_sqlalchemy_exception():
            instance = await self._attach_to_session(data)
            await self._session.flush()
            await self._session.refresh(instance)
            self._session.expunge(instance)
            return instance

    async def delete(self, id_: Any) -> T_model:
        with wrap_sqlalchemy_exception():
            instance = await self.get(id_)
            await self._session.delete(instance)
            await self._session.flush()
            self._session.expunge(instance)
            return instance

    async def get(self, id_: Any) -> T_model:
        with wrap_sqlalchemy_exception():
            self._filter_select_by_kwargs(**{self.id_attribute: id_})
            instance = (await self._execute()).scalar_one_or_none()
            instance = self.check_not_found(instance)
            self._session.expunge(instance)
            return instance

    async def list(self, *filters: "FilterTypes", **kwargs: Any) -> list[T_model]:
        for f in filters:
            match f:
                case LimitOffset(limit, offset):
                    self._apply_limit_offset_pagination(limit, offset)  # noqa: F821
                case BeforeAfter(field_name, before, after):
                    self._filter_on_datetime_field(field_name, before, after)  # noqa: F821
                case CollectionFilter(field_name, values):
                    self._filter_in_collection(field_name, values)  # noqa: F821
        self._filter_select_by_kwargs(**kwargs)

        with wrap_sqlalchemy_exception():
            result = await self._execute()
            instances = list(result.scalars())
            for instance in instances:
                self._session.expunge(instance)
            return instances

    async def update(self, data: T_model) -> T_model:
        with wrap_sqlalchemy_exception():
            id_ = self.get_id_attribute_value(data)
            # this will raise for not found, and will put the item in the session
            await self.get(id_)
            # this will merge the inbound data to the instance we just put in the session
            instance = await self._attach_to_session(data, strategy="merge")
            await self._session.flush()
            await self._session.refresh(instance)
            self._session.expunge(instance)
            return instance

    async def upsert(self, data: T_model) -> T_model:
        with wrap_sqlalchemy_exception():
            instance = await self._attach_to_session(data, strategy="merge")
            await self._session.flush()
            await self._session.refresh(instance)
            self._session.expunge(instance)
            return instance

    # the following is all sqlalchemy implementation detail, and shouldn't be directly accessed

    def _apply_limit_offset_pagination(self, limit: int, offset: int) -> None:
        self._select = self._select.limit(limit).offset(offset)

    async def _attach_to_session(self, model: T_model, strategy: Literal["add", "merge"] = "add") -> T_model:
        """Attach detached instance to the session.

        Parameters
        ----------
        model : T_model
            The instance to be attached to the session.
        strategy : Literal["add", "merge"]
            How the instance should be attached.

        Returns
        -------
        T_model
        """
        match strategy:
            case "add":
                self._session.add(model)
            case "merge":
                await self._session.merge(model)
        return model

    async def _execute(self) -> Result[tuple[T_model, ...]]:
        return await self._session.execute(self._select)

    def _filter_in_collection(self, field_name: str, values: abc.Collection[Any]) -> None:
        self._select = self._select.where(getattr(self.model_type, field_name).in_(values))

    def _filter_on_datetime_field(self, field_name: str, before: "datetime | None", after: "datetime | None") -> None:
        field = getattr(self.model_type, field_name)
        if before is not None:
            self._select = self._select.where(field < before)
        if after is not None:
            self._select = self._select.where(field > before)

    def _filter_select_by_kwargs(self, **kwargs: Any) -> None:
        for k, v in kwargs.items():
            self._select = self._select.where(getattr(self.model_type, k) == v)
