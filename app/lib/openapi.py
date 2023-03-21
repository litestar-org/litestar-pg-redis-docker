from litestar.openapi.config import OpenAPIConfig
from litestar.openapi.spec.contact import Contact

from . import settings

config = OpenAPIConfig(
    title=settings.openapi.TITLE or settings.app.NAME,
    version=settings.openapi.VERSION,
    contact=Contact(name=settings.openapi.CONTACT_NAME, email=settings.openapi.CONTACT_EMAIL),
    use_handler_docstrings=True,
)
"""OpenAPI config for app."""
