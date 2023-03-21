from logging import LogRecord

from litestar.status_codes import HTTP_200_OK, HTTP_503_SERVICE_UNAVAILABLE

from app.lib import logging, settings


def test_access_log_filter_status_ok() -> None:
    log_record = LogRecord(
        name="test.log",
        level=1,
        pathname="pathname",
        lineno=1,
        msg="message",
        args=("", settings.api.HEALTH_PATH, "", HTTP_200_OK),
        exc_info=None,
    )
    log_filter = logging.AccessLogFilter(path_re=settings.api.HEALTH_PATH)
    assert log_filter.filter(log_record) is False


def test_access_log_filter_status_not_ok() -> None:
    log_record = LogRecord(
        name="test.log",
        level=1,
        pathname="pathname",
        lineno=1,
        msg="message",
        args=("", settings.api.HEALTH_PATH, "", HTTP_503_SERVICE_UNAVAILABLE),
        exc_info=None,
    )
    log_filter = logging.AccessLogFilter(path_re=settings.api.HEALTH_PATH)
    assert log_filter.filter(log_record) is True
