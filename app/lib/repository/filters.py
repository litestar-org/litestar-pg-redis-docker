from collections import abc
from dataclasses import dataclass
from datetime import datetime
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass
class BeforeAfter:
    """Data required to filter a query on a `datetime` column."""

    field_name: str
    """Name of the model attribute to filter on."""
    before: datetime | None
    """Filter results where field earlier than this [datetime][datetime.datetime]"""
    after: datetime | None
    """Filter results where field later than this [datetime][datetime.datetime]"""


@dataclass
class CollectionFilter(Generic[T]):
    """Data required to construct a `WHERE ...

    IN (...)` clause.
    """

    field_name: str
    """Name of the model attribute to filter on."""
    values: abc.Collection[T]
    """Values for `IN` clause."""


@dataclass
class LimitOffset:
    """Data required to add limit/offset filtering to a query."""

    limit: int
    """Value for `LIMIT` clause of query."""
    offset: int
    """Value for `OFFSET` clause of query."""
