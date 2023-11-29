from datetime import date
from typing import Annotated
from uuid import UUID

from litestar.contrib.sqlalchemy.base import UUIDAuditBase
from litestar.contrib.sqlalchemy.dto import SQLAlchemyDTO
from litestar.contrib.sqlalchemy.repository import SQLAlchemyAsyncRepository
from litestar.dto import DTOConfig, Mark, dto_field
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.lib import service

from . import countries

__all__ = [
    "Author",
    "ReadDTO",
    "Repository",
    "Service",
    "WriteDTO",
]


class Author(UUIDAuditBase):
    name: Mapped[str]
    dob: Mapped[date]
    country_id: Mapped[UUID | None] = mapped_column(ForeignKey("country.id"))
    nationality: Mapped[countries.Country | None] = relationship(lazy="joined", info=dto_field(Mark.READ_ONLY))


class Repository(SQLAlchemyAsyncRepository[Author]):
    model_type = Author


class Service(service.Service[Author]):
    repository_type = Repository


write_config = DTOConfig(exclude={"created_at", "updated_at", "nationality"})
WriteDTO = SQLAlchemyDTO[Annotated[Author, write_config]]
ReadDTO = SQLAlchemyDTO[Author]
