from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import MetaData
from sqlalchemy.dialects import postgresql as pg
from sqlalchemy.event import listens_for
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    Session,
    declared_attr,
    mapped_column,
    registry,
)

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}
"""
Templates for automated constraint name generation.
"""


@listens_for(Session, "before_flush")
def touch_updated_timestamp(session: Session, *_: Any) -> None:
    """Called from SQLAlchemy's.

    [`before_flush`][sqlalchemy.orm.SessionEvents.before_flush] event to bump
    the `updated` timestamp on modified instances.

    Parameters
    ----------
    session : Session
        The sync [`Session`][sqlalchemy.orm.Session] instance that underlies the async session.
    """
    for instance in session.dirty:
        instance.updated = datetime.now()


class Base(DeclarativeBase):
    """Base for all SQLAlchemy declarative models.

    Attributes
    ----------
    created : Mapped[datetime]
        Date/time of instance creation.
    updated : Mapped[datetime]
        Date/time of last instance update.
    """

    registry = registry(
        metadata=MetaData(naming_convention=convention),
        type_annotation_map={UUID: pg.UUID, dict: pg.JSONB},
    )

    id: Mapped[UUID] = mapped_column(default=uuid4, primary_key=True)
    created: Mapped[datetime] = mapped_column(default=datetime.now)
    updated: Mapped[datetime] = mapped_column(default=datetime.now)

    # noinspection PyMethodParameters
    @declared_attr.directive
    def __tablename__(cls) -> str:  # pylint: disable=no-self-argument
        return cls.__name__.lower()
