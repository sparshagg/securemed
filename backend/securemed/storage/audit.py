"""Hash-chained JSONL audit log."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from securemed.crypto.hashing import sha256_json_hex

GENESIS_HASH = "0" * 64


class AuditLogVerificationError(ValueError):
    """Raised when the audit chain is malformed or tampered."""


@dataclass(frozen=True)
class AuditVerificationResult:
    valid: bool
    entries_checked: int
    last_hash: str


def _entry_hash_material(entry: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in entry.items() if key != "entry_hash"}


def compute_entry_hash(entry: dict[str, Any]) -> str:
    """Compute the canonical hash for an audit entry."""
    return sha256_json_hex(_entry_hash_material(entry))


def read_audit_entries(path: Path) -> list[dict[str, Any]]:
    """Read JSONL audit entries from disk."""
    if not path.exists():
        return []

    entries: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                entries.append(json.loads(stripped))
            except json.JSONDecodeError as exc:
                raise AuditLogVerificationError(
                    f"audit entry {line_number} is not valid JSON",
                ) from exc
    return entries


def append_audit_event(
    path: Path,
    *,
    record_id: str,
    provider_id: str,
    credential_commitment: str,
    action: str,
    reason: str,
    release_id: str | None = None,
    timestamp: str | None = None,
    event_id: str | None = None,
) -> dict[str, Any]:
    """Append a grant/deny audit event without plaintext or secret material."""
    entries = read_audit_entries(path)
    previous_hash = verify_audit_log(path).last_hash if entries else GENESIS_HASH
    entry: dict[str, Any] = {
        "event_id": event_id or f"evt_{uuid4().hex}",
        "timestamp": timestamp or datetime.now(UTC).isoformat(),
        "record_id": record_id,
        "provider_id": provider_id,
        "credential_commitment": credential_commitment,
        "action": action,
        "reason": reason,
        "release_id": release_id,
        "previous_hash": previous_hash,
    }
    entry["entry_hash"] = compute_entry_hash(entry)

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, sort_keys=True, separators=(",", ":")))
        handle.write("\n")

    return entry


def verify_audit_log(path: Path) -> AuditVerificationResult:
    """Verify every previous-hash link and entry hash in a JSONL audit log."""
    previous_hash = GENESIS_HASH
    entries = read_audit_entries(path)

    for index, entry in enumerate(entries, start=1):
        if entry.get("previous_hash") != previous_hash:
            raise AuditLogVerificationError(
                f"audit entry {index} previous_hash does not match chain",
            )
        expected_hash = compute_entry_hash(entry)
        if entry.get("entry_hash") != expected_hash:
            raise AuditLogVerificationError(
                f"audit entry {index} entry_hash does not match entry contents",
            )
        previous_hash = expected_hash

    return AuditVerificationResult(
        valid=True,
        entries_checked=len(entries),
        last_hash=previous_hash,
    )
