from collections import abc
from datetime import datetime
from uuid import uuid4

import pytest
from starlite import Starlite
from starlite.testing import RequestFactory

from app.lib import dependencies
from app.lib.repository.filters import BeforeAfter, CollectionFilter, LimitOffset
from app.lib.users import User


async def test_provide_user_dependency() -> None:
    user = User()
    request = RequestFactory(app=Starlite(route_handlers=[])).get("/", user=user)
    assert await dependencies.provide_user(request) is user


def test_id_filter() -> None:
    ids = [uuid4() for _ in range(3)]
    assert dependencies.id_filter(ids) == CollectionFilter(field_name="id", values=ids)


@pytest.mark.parametrize(
    ("filter_", "field_name"), [(dependencies.created_filter, "created"), (dependencies.updated_filter, "updated")]
)
def test_before_after_filters(filter_: abc.Callable[[datetime, datetime], BeforeAfter], field_name: str) -> None:
    assert filter_(datetime.max, datetime.min) == BeforeAfter(
        field_name=field_name, before=datetime.max, after=datetime.min
    )


def test_limit_offset_pagination() -> None:
    assert dependencies.limit_offset_pagination(10, 100) == LimitOffset(100, 900)
