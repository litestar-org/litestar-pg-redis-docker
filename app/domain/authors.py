from datetime import date
from email.message import EmailMessage

from sqlalchemy.orm import Mapped

from app.lib import dto, email, orm, service, settings
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

    @staticmethod
    async def send_author_created_email(message_content: str) -> None:
        """Sends an email to alert that a new `Author` has been created.

        Args:
            message_content: The body of the email.
        """
        message = EmailMessage()
        message["From"] = settings.email.SENDER
        message["To"] = settings.email.RECIPIENT
        message["Subject"] = settings.email.NEW_AUTHOR_SUBJECT
        message.set_content(message_content)
        async with email.client:
            await email.client.send_message(message)


CreateDTO = dto.factory("AuthorCreateDTO", Author, purpose=dto.Purpose.write, exclude={"id"})
ReadDTO = dto.factory("AuthorReadDTO", Author, purpose=dto.Purpose.read)
WriteDTO = dto.factory("AuthorWriteDTO", Author, purpose=dto.Purpose.write)
