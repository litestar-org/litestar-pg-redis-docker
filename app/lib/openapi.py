from pydantic_openapi_schema.v3_1_0 import Contact
from starlite.config.openapi import OpenAPIConfig

from . import settings
from .auth import jwt_auth

config = OpenAPIConfig(
    title=settings.openapi.TITLE or settings.app.NAME,
    version=settings.openapi.VERSION,
    contact=Contact(name=settings.openapi.CONTACT_NAME, email=settings.openapi.CONTACT_EMAIL),
    components=[jwt_auth.openapi_components],
    security=[jwt_auth.security_requirement],
    use_handler_docstrings=True,
)
"""OpenAPI config for app, see.

[OpenAPISettings][starlite_saqpg.config.OpenAPISettings]
"""
