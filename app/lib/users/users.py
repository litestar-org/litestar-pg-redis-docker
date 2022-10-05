from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy.dialects import postgresql as pg
from sqlalchemy.orm import Mapped, mapped_column

from app.lib import orm, service
from app.lib.repository.sqlalchemy import SQLAlchemyRepository

from .types import UserTypes

if TYPE_CHECKING:
    from uuid import UUID


__all__ = [
    "User",
    "Repository",
    "Service",
]


class User(orm.Base):
    name: Mapped[str]
    joined: Mapped[date] = mapped_column(default=date.today)
    type: Mapped[UserTypes] = mapped_column(pg.ENUM(UserTypes, name="user-types-enum"), default=UserTypes.regular)


class Repository(SQLAlchemyRepository[User]):
    model_type = User


class Service(service.Service[User]):
    async def authorize_list(self) -> None:
        if self.user.type is not UserTypes.admin:
            raise service.UnauthorizedException("Only admin can view all users")
        return await super().authorize_list()

    async def authorize_get(self, id_: "UUID") -> None:
        if self.user.type is not UserTypes.admin and self.user.id != id_:
            raise service.UnauthorizedException("Only admin can view other user detail")
        return await super().authorize_get(id_)

    async def authorize_create(self, data: User) -> User:
        if self.user.type is not UserTypes.admin:
            data.type = UserTypes.regular
        data = await super().authorize_create(data)
        return data

    async def authorize_delete(self, id_: "UUID") -> None:
        if self.user.type is not UserTypes.admin and self.user.id != id_:
            raise service.UnauthorizedException("Only admin can view other user detail")
        return await super().authorize_delete(id_)
