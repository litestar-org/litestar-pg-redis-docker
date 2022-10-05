import sentry_sdk
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

from . import settings


def configure() -> None:
    """Callback to configure sentry on app startup.

    See [SentrySettings][starlite_saqpg.config.SentrySettings].
    """
    sentry_sdk.init(
        dsn=settings.sentry.DSN,
        environment=settings.app.ENVIRONMENT,
        release=settings.app.BUILD_NUMBER,
        integrations=[SqlalchemyIntegration()],
        traces_sample_rate=settings.sentry.TRACES_SAMPLE_RATE,
    )
