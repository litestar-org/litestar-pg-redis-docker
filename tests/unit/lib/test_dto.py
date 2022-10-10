# pylint: disable=redefined-outer-name
from datetime import date, datetime
from typing import Any, ClassVar
from uuid import UUID, uuid4

import pytest
from sqlalchemy import func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from app.domain.authors import Author
from app.lib import dto


def test_model_write_dto(raw_authors: list[dict[str, Any]]) -> None:
    dto_type = dto.factory("AuthorDTO", Author, dto.Purpose.write)
    assert dto_type.__fields__.keys() == {"name", "dob"}
    inst = dto_type(**raw_authors[0])
    model = Author(**inst.dict(exclude_unset=True))
    assert {k: v for k, v in model.__dict__.items() if not k.startswith("_")} == {
        "name": "Agatha Christie",
        "dob": date(1890, 9, 15),
    }


def test_model_read_dto(raw_authors: list[dict[str, Any]]) -> None:
    dto_type = dto.factory("AuthorDTO", Author, dto.Purpose.read)
    assert dto_type.__fields__.keys() == {"name", "dob", "id", "created", "updated"}
    inst = dto_type(**raw_authors[1])
    model = Author(**inst.dict(exclude_unset=True))
    assert {k: v for k, v in model.__dict__.items() if not k.startswith("_")} == {
        "name": "Leo Tolstoy",
        "dob": date(1828, 9, 9),
        "id": UUID("5ef29f3c-3560-4d15-ba6b-a2e5c721e4d2"),
        "updated": datetime(1, 1, 1, 0, 0),
        "created": datetime(1, 1, 1, 0, 0),
    }


def test_dto_exclude() -> None:
    dto_type = dto.factory("AuthorDTO", Author, dto.Purpose.read, exclude={"id"})
    assert dto_type.__fields__.keys() == {"name", "dob", "created", "updated"}


@pytest.fixture()
def base() -> type[DeclarativeBase]:
    """Declarative base for test models.

    Need a new base for every test, otherwise will get errors to do with
    tables already existing in the mapper when we reuse models of the
    same name across multiple tests.
    """

    class Base(DeclarativeBase):
        id: Mapped[int] = mapped_column(primary_key=True)

    return Base


@pytest.mark.parametrize(("purpose", "default", "exp"), [(dto.Purpose.write, 3, 3), (dto.Purpose.read, 3, None)])
def test_write_dto_for_model_field_scalar_default(
    purpose: dto.Purpose, default: Any, exp: Any, base: type[DeclarativeBase]
) -> None:
    class Model(base):
        __tablename__ = "smth"
        field: Mapped[int] = mapped_column(default=default)

    dto_model = dto.factory("DTO", Model, purpose=purpose)
    assert dto_model.__fields__["field"].default == exp


def test_write_dto_for_model_field_factory_default(base: type[DeclarativeBase]) -> None:
    class Model(base):
        __tablename__ = "smth"
        field: Mapped[UUID] = mapped_column(default=uuid4)

    dto_model = dto.factory("DTO", Model, purpose=dto.Purpose.write)

    assert isinstance(dto_model.__fields__["field"].default_factory(), UUID)


def test_read_dto_for_model_field_factory_default(base: type[DeclarativeBase]) -> None:
    class Model(base):
        __tablename__ = "smth"
        field: Mapped[UUID] = mapped_column(default=uuid4)

    dto_model = dto.factory("DTO", Model, purpose=dto.Purpose.read)

    assert dto_model.__fields__["field"].default_factory is None


def test_read_dto_for_model_field_unsupported_default(base: type[DeclarativeBase]) -> None:
    class Model(base):
        __tablename__ = "smth"
        field: Mapped[datetime] = mapped_column(default=func.now())

    with pytest.raises(ValueError):  # noqa: PT011
        dto.factory("DTO", Model, purpose=dto.Purpose.write)


@pytest.mark.parametrize("purpose", [dto.Purpose.write, dto.Purpose.read])
def test_dto_for_private_model_field(purpose: dto.Purpose, base: type[DeclarativeBase]) -> None:
    class Model(base):
        __tablename__ = "smth"
        field: Mapped[datetime] = mapped_column(default=datetime.now(), info={"dto": dto.Mode.private})

    dto_model = dto.factory("DTO", Model, purpose=purpose)
    assert "field" not in dto_model.__fields__


@pytest.mark.parametrize("purpose", [dto.Purpose.write, dto.Purpose.read])
def test_dto_for_non_mapped_model_field(purpose: dto.Purpose, base: type[DeclarativeBase]) -> None:
    class Model(base):
        __tablename__ = "smth"
        field: ClassVar[datetime]

    dto_model = dto.factory("DTO", Model, purpose=purpose)
    assert "field" not in dto_model.__fields__
