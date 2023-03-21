from __future__ import annotations

from typing import TYPE_CHECKING, Any, Generic

from litestar.contrib.sqlalchemy.repository import ModelT

__all__ = ["Service", "ServiceError"]


if TYPE_CHECKING:
    from litestar.contrib.repository.abc import AbstractAsyncRepository, FilterTypes


class ServiceError(Exception):
    """Base class for `Service` related exceptions."""


class Service(Generic[ModelT]):
    def __init__(self, repository: AbstractAsyncRepository[ModelT]) -> None:
        """Generic Service object.

        Args:
            repository: Instance conforming to `AbstractRepository` interface.
        """
        self.repository = repository

    async def create(self, data: ModelT) -> ModelT:
        """Wraps repository instance creation.

        Args:
            data: Representation to be created.

        Returns:
            Representation of created instance.
        """
        return await self.repository.add(data)

    async def list(self, *filters: FilterTypes, **kwargs: Any) -> list[ModelT]:
        """Wraps repository scalars operation.

        Args:
            *filters: Collection route filters.
            **kwargs: Keyword arguments for attribute based filtering.

        Returns:
            The list of instances retrieved from the repository.
        """
        return await self.repository.list(*filters, **kwargs)

    async def update(self, id_: Any, data: ModelT) -> ModelT:
        """Wraps repository update operation.

        Args:
            id_: Identifier of item to be updated.
            data: Representation to be updated.

        Returns:
            Updated representation.
        """
        return await self.repository.update(data)

    async def upsert(self, id_: Any, data: ModelT) -> ModelT:
        """Wraps repository upsert operation.

        Args:
            id_: Identifier of the object for upsert.
            data: Representation for upsert.

        Returns:
        -------
            Updated or created representation.
        """
        return await self.repository.upsert(data)

    async def get(self, id_: Any) -> ModelT:
        """Wraps repository scalar operation.

        Args:
            id_: Identifier of instance to be retrieved.

        Returns:
            Representation of instance with identifier `id_`.
        """
        return await self.repository.get(id_)

    async def delete(self, id_: Any) -> ModelT:
        """Wraps repository delete operation.

        Args:
            id_: Identifier of instance to be deleted.

        Returns:
            Representation of the deleted instance.
        """
        return await self.repository.delete(id_)
