from collections import abc
from datetime import datetime
from typing import Any, Generic, TypeVar
from uuid import uuid4

from app.lib.orm import Base
from app.lib.repository.abc import AbstractRepository
from app.lib.repository.types import FilterTypes

T_base = TypeVar("T_base", bound=Base)


class GenericMockRepository(AbstractRepository[T_base], Generic[T_base]):
    collection: abc.MutableMapping[abc.Hashable, T_base] = {}

    def __init__(self, id_factory: abc.Callable[[], Any] = uuid4, **_: Any) -> None:
        self._id_factory = id_factory

    def _find_or_raise_not_found(self, id_: Any) -> T_base:
        return self.check_not_found(self.collection.get(id_))

    def _set_id_attribute_value(self, item: T_base, value: Any) -> None:
        setattr(item, self.id_attribute, value)

    async def add(self, data: T_base) -> T_base:
        assert await self.get_id_attribute_value(data) is None, "received identified instance"
        now = datetime.now()
        data.updated = data.created = now
        id_ = self._id_factory()
        self._set_id_attribute_value(data, id_)
        self.collection[id_] = data
        return data

    async def delete(self, id_: Any) -> T_base:
        item = self._find_or_raise_not_found(id_)
        del self.collection[id_]
        return item

    async def get(self, id_: Any) -> T_base:
        return self._find_or_raise_not_found(id_)

    async def list(self, *filters: FilterTypes, **kwargs: Any) -> list[T_base]:
        # TODO: support filters here  # pylint: disable=fixme
        return list(self.collection.values())

    async def update(self, data: T_base) -> T_base:
        item = self._find_or_raise_not_found(await self.get_id_attribute_value(data))
        # should never be modifiable
        del data.created
        data.updated = datetime.now()
        for k, v in data.__dict__.items():
            if k.startswith("_"):
                continue
            setattr(item, k, v)
        return item

    async def upsert(self, data: T_base) -> T_base:
        if await self.get_id_attribute_value(data) is None:
            return await self.add(data)
        return await self.update(data)
