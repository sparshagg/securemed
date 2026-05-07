"""JSON-backed local state for the SecureMed demo."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class StateNotFoundError(ValueError):
    """Raised when required demo state is missing."""


@dataclass(frozen=True)
class DemoPaths:
    data_dir: Path = Path("data")

    @property
    def records_path(self) -> Path:
        return self.data_dir / "records.json"

    @property
    def record_keys_path(self) -> Path:
        return self.data_dir / "private" / "record_keys.json"

    @property
    def provider_private_path(self) -> Path:
        return self.data_dir / "private" / "provider_private.json"

    @property
    def providers_path(self) -> Path:
        return self.data_dir / "providers.json"

    @property
    def consent_path(self) -> Path:
        return self.data_dir / "consent_policies.json"

    @property
    def revoked_path(self) -> Path:
        return self.data_dir / "revoked_credentials.json"

    @property
    def audit_path(self) -> Path:
        return self.data_dir / "audit.jsonl"

    @property
    def zkp_dir(self) -> Path:
        return self.data_dir / "zkp"


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


class DemoStore:
    """Simple JSON store for local prototype data."""

    def __init__(self, paths: DemoPaths | None = None) -> None:
        self.paths = paths or DemoPaths()

    def ensure_dirs(self) -> None:
        self.paths.data_dir.mkdir(parents=True, exist_ok=True)
        (self.paths.data_dir / "private").mkdir(parents=True, exist_ok=True)
        self.paths.zkp_dir.mkdir(parents=True, exist_ok=True)

    def read_records(self) -> dict[str, Any]:
        return dict(read_json(self.paths.records_path, {}))

    def write_records(self, records: dict[str, Any]) -> None:
        write_json(self.paths.records_path, records)

    def save_record(self, record_id: str, record: dict[str, Any]) -> None:
        records = self.read_records()
        records[record_id] = record
        self.write_records(records)

    def get_record(self, record_id: str) -> dict[str, Any]:
        record = self.read_records().get(record_id)
        if record is None:
            raise StateNotFoundError(f"record not found: {record_id}")
        return dict(record)

    def read_record_keys(self) -> dict[str, str]:
        return dict(read_json(self.paths.record_keys_path, {}))

    def write_record_keys(self, keys: dict[str, str]) -> None:
        write_json(self.paths.record_keys_path, keys)

    def save_record_key(self, record_id: str, dek_b64: str) -> None:
        keys = self.read_record_keys()
        keys[record_id] = dek_b64
        self.write_record_keys(keys)

    def get_record_key(self, record_id: str) -> str:
        key = self.read_record_keys().get(record_id)
        if key is None:
            raise StateNotFoundError(f"record key not found: {record_id}")
        return str(key)

    def read_providers(self) -> dict[str, Any]:
        return dict(read_json(self.paths.providers_path, {}))

    def write_providers(self, providers: dict[str, Any]) -> None:
        write_json(self.paths.providers_path, providers)

    def save_provider(self, provider_id: str, provider: dict[str, Any]) -> None:
        providers = self.read_providers()
        providers[provider_id] = provider
        self.write_providers(providers)

    def get_provider(self, provider_id: str) -> dict[str, Any]:
        provider = self.read_providers().get(provider_id)
        if provider is None:
            raise StateNotFoundError(f"provider not found: {provider_id}")
        return dict(provider)

    def read_provider_private(self) -> dict[str, Any]:
        return dict(read_json(self.paths.provider_private_path, {}))

    def write_provider_private(self, value: dict[str, Any]) -> None:
        write_json(self.paths.provider_private_path, value)

    def read_consent_policies(self) -> list[dict[str, Any]]:
        return list(read_json(self.paths.consent_path, []))

    def write_consent_policies(self, value: list[dict[str, Any]]) -> None:
        write_json(self.paths.consent_path, value)

    def read_revoked_credentials(self) -> list[dict[str, Any]]:
        return list(read_json(self.paths.revoked_path, []))

    def write_revoked_credentials(self, value: list[dict[str, Any]]) -> None:
        write_json(self.paths.revoked_path, value)
