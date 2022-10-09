import json
from email.message import EmailMessage

import aiosmtplib


async def author_created(_: dict, *, data: dict) -> dict:
    """Send an email when a new Author is created.

    Args:
        _: SAQ context.
        data: The created author object.

    Returns:
        The author object.
    """
    message = EmailMessage()
    message["From"] = "root@localhost"
    message["To"] = "somebody@example.com"
    message["Subject"] = "New Author Added"
    message.set_content(json.dumps(data))
    await aiosmtplib.send(message, hostname="mailhog", port=1025)
    return data
