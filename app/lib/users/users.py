from datetime import date

from sqlalchemy.dialects import postgresql as pg
from sqlalchemy.orm import Mapped, mapped_column

from app.lib import orm, service
from app.lib.repository.sqlalchemy import SQLAlchemyRepository

from .types import UserTypes

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


Service = service.Service[User]
