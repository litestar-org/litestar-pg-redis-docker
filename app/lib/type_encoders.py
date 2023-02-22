"""A mapping of types to serializer callables."""
from __future__ import annotations

from typing import TYPE_CHECKING

from asyncpg.pgproto import pgproto
from starlite.utils.serialization import DEFAULT_TYPE_ENCODERS

if TYPE_CHECKING:
    from starlite.types import TypeEncodersMap


type_encoders_map: TypeEncodersMap = {**DEFAULT_TYPE_ENCODERS, pgproto.UUID: str}
