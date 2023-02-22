"""Tests for the SAQ async worker functionality."""
from __future__ import annotations

from asyncpg.pgproto import pgproto
from pydantic import BaseModel

from app.lib import worker


def test_worker_decoder_handles_pgproto_uuid() -> None:
    """Test that the decoder can handle pgproto.UUID instances."""
    pg_uuid = pgproto.UUID("0448bde2-7c69-4e6b-9c03-7b217e3b563d")
    encoded = worker.encoder.encode(pg_uuid)
    # msgpack encoded
    assert encoded == b'"0448bde2-7c69-4e6b-9c03-7b217e3b563d"'


def test_worker_decoder_handles_pydantic_models() -> None:
    """Test that the decoder we use for SAQ will encode a pydantic model."""

    class Model(BaseModel):
        a: str
        b: int
        c: float

    pydantic_model = Model(a="a", b=1, c=2.34)
    encoded = worker.encoder.encode(pydantic_model)
    assert encoded == b'{"a":"a","b":1,"c":2.34}'
