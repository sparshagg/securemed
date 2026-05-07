"""Small encoding helpers for JSON-safe cryptographic payloads."""

from __future__ import annotations

import base64


def b64encode(data: bytes) -> str:
    """Encode bytes as ASCII base64."""
    return base64.b64encode(data).decode("ascii")


def b64decode(value: str) -> bytes:
    """Decode ASCII base64 into bytes."""
    return base64.b64decode(value.encode("ascii"))
