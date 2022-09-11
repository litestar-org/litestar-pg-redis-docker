import re
from datetime import datetime
from uuid import UUID

from sqlalchemy import MetaData
from sqlalchemy.dialects import postgresql as pg
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm.decl_api import DeclarativeBase, declared_attr, registry

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    """Base for all SQLAlchemy declarative models.

    Attributes
    ----------
    created : Mapped[datetime]
        Date/time of instance creation.
    updated : Mapped[datetime]
        Date/time of last instance update.
    """

    table_name_pattern = re.compile(r"(?<!^)(?=[A-Z])")

    # noinspection PyMethodParameters
    @declared_attr.directive
    def __tablename__(cls) -> str:  # pylint: disable=no-self-argument
        return re.sub(cls.table_name_pattern, "_", cls.__name__).lower()

    registry = registry(
        metadata=MetaData(naming_convention=convention),
        type_annotation_map={UUID: pg.UUID, dict: pg.JSONB},
    )
    id: Mapped[UUID] = mapped_column(primary_key=True)
    created: Mapped[datetime] = mapped_column(default=datetime.now)
    updated: Mapped[datetime] = mapped_column(default=datetime.now)
