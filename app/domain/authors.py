from datetime import date

from sqlalchemy.orm import Mapped

from app.lib import orm
from app.lib.repository.sqlalchemy import SQLAlchemyRepository


class Author(orm.Base):
    name: Mapped[str]
    dob: Mapped[date]


class Repository(SQLAlchemyRepository[Author]):
    model_type = Author
