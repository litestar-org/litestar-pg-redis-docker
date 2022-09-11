from uuid import UUID

from sqlalchemy import Enum, ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.model import InProviderDomain

from .types import EntitiesEnum


class Entity(InProviderDomain):
    name: Mapped[str] = mapped_column(nullable=False)
    type: Mapped[Enum] = mapped_column(Enum(EntitiesEnum, create_constraint=False), nullable=False)
    owner_id: Mapped[UUID | None] = mapped_column(ForeignKey("entity.id"), index=True, nullable=True)
    ryno_id: Mapped[int] = mapped_column(index=True, nullable=True)
    extra: Mapped[dict] = mapped_column(server_default=text("'{}'::jsonb"))
