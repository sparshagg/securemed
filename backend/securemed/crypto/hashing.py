"""Hash helpers used by manifests and audit entries."""

from __future__ import annotations

import hashlib
from typing import Any

from securemed.crypto.canonical import canonical_json_bytes


def sha256_hex(data: bytes) -> str:
    """Return a SHA-256 hex digest for bytes."""
    return hashlib.sha256(data).hexdigest()


def sha256_json_hex(value: Any) -> str:
    """Return a SHA-256 hex digest for canonical JSON."""
    return sha256_hex(canonical_json_bytes(value))
