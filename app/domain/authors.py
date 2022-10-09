from datetime import date

from sqlalchemy.orm import Mapped

from app.lib import dto, orm, service
from app.lib.repository.sqlalchemy import SQLAlchemyRepository
from app.lib.worker import queue


class Author(orm.Base):
    name: Mapped[str]
    dob: Mapped[date]


class Repository(SQLAlchemyRepository[Author]):
    model_type = Author


class Service(service.Service[Author]):
    async def create(self, data: Author) -> Author:
        created = await super().create(data)
        await queue.enqueue("author_created", data=ReadDTO.from_orm(created).dict())
        return data


ReadDTO = dto.factory("AuthorReadDTO", Author, purpose=dto.Purpose.read)
WriteDTO = dto.factory("AuthorWriteDTO", Author, purpose=dto.Purpose.write)
