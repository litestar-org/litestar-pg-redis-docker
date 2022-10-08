from datetime import date

from sqlalchemy.orm import Mapped

from app.lib import dto, orm
from app.lib.repository.sqlalchemy import SQLAlchemyRepository


class Author(orm.Base):
    name: Mapped[str]
    dob: Mapped[date]


class Repository(SQLAlchemyRepository[Author]):
    model_type = Author


ReadDTO = dto.factory("AuthorReadDTO", Author, purpose=dto.Purpose.read)
WriteDTO = dto.factory("AuthorWriteDTO", Author, purpose=dto.Purpose.write)
