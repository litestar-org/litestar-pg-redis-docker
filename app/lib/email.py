from aiosmtplib import SMTP

from . import settings

client = SMTP(
    hostname=settings.email.HOST,
    port=settings.email.PORT,
)
