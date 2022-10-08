from datetime import date, datetime
from typing import Any
from uuid import UUID

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
