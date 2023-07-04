"""All configuration via environment.

Take note of the environment variable prefixes required for each
settings class, except `AppSettings`.
"""
from typing import Literal

from pydantic import AnyUrl, BaseSettings, PostgresDsn

__all__ = [
    "APISettings",
    "AppSettings",
    "DatabaseSettings",
    "EmailSettings",
    "OpenAPISettings",
    "RedisSettings",
    "SentrySettings",
    "ServerSettings",
]


# noinspection PyUnresolvedReferences


class BaseEnvSettings(BaseSettings):
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class AppSettings(BaseEnvSettings):
    """Generic application settings. These settings are returned as json by the
    healthcheck endpoint, so do not include any sensitive values here, or if
    you do ensure to exclude them from serialization in the `Config` object.

    Attributes:
    ----------
    BUILD_NUMBER : str
        Identity of the CI build of current app instance.
    DEBUG : bool
        If `True` runs `Litestar` in debug mode.
    ENVIRONMENT : str
        "dev", "prod", etc.
    LOG_LEVEL : str
        Stdlib log level names, "DEBUG", "INFO", etc.
    NAME : str
        App name.
    """

    class Config:
        case_sensitive = True

    BUILD_NUMBER: str = "0"
    DEBUG: bool = False
    ENVIRONMENT: str = "local"
    LOG_LEVEL: str = "INFO"
    NAME: str = "litestar-pg-redis-docker"

    @property
    def slug(self) -> str:
        """A slugified name.

        Returns:
        -------
        str
            `self.NAME`, all lowercase and hyphens instead of spaces.
        """
        return "-".join(s.lower() for s in self.NAME.split())


# noinspection PyUnresolvedReferences
class APISettings(BaseEnvSettings):
    """API specific configuration.

    Prefix all environment variables with `API_`, e.g., `API_CACHE_EXPIRATION`.

    Attributes:
    ----------
    CACHE_EXPIRATION : int
        Default cache key expiration in seconds.
    DEFAULT_PAGINATION_LIMIT : int
        Max records received for collection routes.
    """

    class Config:
        env_prefix = "API_"
        case_sensitive = True

    CACHE_EXPIRATION: int = 60
    DB_SESSION_DEPENDENCY_KEY: str = "db_session"
    DEFAULT_PAGINATION_LIMIT: int = 100
    DEFAULT_USER_NAME: str = "__default_user__"
    HEALTH_PATH: str = "/health"
    SECRET_KEY: str = "abc123"
    USER_DEPENDENCY_KEY: str = "user"


# noinspection PyUnresolvedReferences
class OpenAPISettings(BaseEnvSettings):
    """Configures OpenAPI for the application.

    Prefix all environment variables with `OPENAPI_`, e.g., `OPENAPI_TITLE`.

    Attributes:
    ----------
    TITLE : str
        OpenAPI document title.
    VERSION : str
        OpenAPI document version.
    CONTACT_NAME : str
        OpenAPI document contact name.
    CONTACT_EMAIL : str
        OpenAPI document contact email.
    """

    class Config:
        env_prefix = "OPENAPI_"
        case_sensitive = True

    TITLE: str | None = "My Litestar App"
    VERSION: str = "0.1.0"
    CONTACT_NAME: str = "My Name"
    CONTACT_EMAIL: str = "some_human@some_domain.com"


# noinspection PyUnresolvedReferences
class DatabaseSettings(BaseEnvSettings):
    """Configures the database for the application.

    Prefix all environment variables with `DB_`, e.g., `DB_URL`.

    Attributes:
    ----------
    ECHO : bool
        Enables SQLAlchemy engine logs.
    URL : PostgresDsn
        URL for database connection.
    """

    class Config:
        env_prefix = "DB_"
        case_sensitive = True

    ECHO: bool = False
    ECHO_POOL: bool | Literal["debug"] = False
    POOL_DISABLE: bool = False
    POOL_MAX_OVERFLOW: int = 10
    POOL_SIZE: int = 5
    POOL_TIMEOUT: int = 30
    URL: PostgresDsn = PostgresDsn(  # pyright:ignore
        "postgresql+asyncpg://postgres:postgres@localhost:5432/postgres", scheme="postgresql+asyncpg"
    )


# noinspection PyUnresolvedReferences
class RedisSettings(BaseEnvSettings):
    """Cache settings for the application.

    Prefix all environment variables with `REDIS_`, e.g., `REDIS_URL`.

    Attributes:
    ----------
    URL : AnyUrl
        A redis connection URL.
    """

    class Config:
        env_prefix = "REDIS_"
        case_sensitive = True

    URL: AnyUrl = AnyUrl("redis://localhost:6379/0", scheme="redis")  # pyright:ignore


# noinspection PyUnresolvedReferences
class SentrySettings(BaseEnvSettings):
    """Configures sentry for the application.

    Attributes:
    ----------
    DSN : str
        The sentry DSN. Set as empty string to disable sentry reporting.
    TRACES_SAMPLE_RATE : float
        % of requests traced by sentry, `0.0` means none, `1.0` means all.
    """

    class Config:
        env_prefix = "SENTRY_"
        case_sensitive = True

    DSN: str = ""
    TRACES_SAMPLE_RATE: float = 0.0


# noinspection PyUnresolvedReferences
class ServerSettings(BaseEnvSettings):
    class Config:
        env_prefix = "UVICORN_"
        case_sensitive = True

    HOST: str = "localhost"
    LOG_LEVEL: str = "info"
    PORT: int = 8000
    RELOAD: bool = True
    KEEPALIVE: int = 65


class EmailSettings(BaseEnvSettings):
    class Config:
        env_prefix = "EMAIL_"
        case_sensitive = True


# `.parse_obj()` thing is a workaround for pyright and pydantic interplay, see:
# https://github.com/pydantic/pydantic/issues/3753#issuecomment-1087417884
api = APISettings.parse_obj({})
app = AppSettings.parse_obj({})
db = DatabaseSettings.parse_obj({})
openapi = OpenAPISettings.parse_obj({})
redis = RedisSettings.parse_obj({})
sentry = SentrySettings.parse_obj({})
server = ServerSettings.parse_obj({})
