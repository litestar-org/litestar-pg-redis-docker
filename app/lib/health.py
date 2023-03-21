import contextlib

from litestar import get
from litestar.contrib.sqlalchemy.repository import SQLAlchemyAsyncRepository
from litestar.exceptions import ServiceUnavailableException
from sqlalchemy.ext.asyncio import AsyncSession

from . import settings
from .settings import AppSettings

__all__ = ["HealthCheckFailure", "health_check"]


class HealthCheckFailure(ServiceUnavailableException):
    """Raise for health check failure."""


@get(path=settings.api.HEALTH_PATH, cache=False, tags=["Misc"])
async def health_check(db_session: AsyncSession) -> AppSettings:
    """Check database available and returns app config info."""
    with contextlib.suppress(Exception):
        if await SQLAlchemyAsyncRepository.check_health(db_session):
            return settings.app
    raise HealthCheckFailure("DB not ready.")
