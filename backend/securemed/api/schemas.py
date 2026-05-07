"""Pydantic schemas for the SecureMed API."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class SetupDemoResponse(BaseModel):
    record_id: str
    provider_id: str
    purpose: str
    provider: dict[str, Any]
    consent: dict[str, Any]
    zkp_input_hint: dict[str, int]
    demo_proof: dict[str, Any] | None = None
    zkp_ready: bool


class ProviderRegistrationRequest(BaseModel):
    provider_id: str = Field(min_length=1)
    provider_label: str = Field(min_length=1)
    x25519_public_key_b64: str = Field(min_length=1)
    credential_commitment: str = Field(min_length=1)
    role_code: int = Field(ge=0)
    status: str = "active"


class ProviderRegistrationResponse(BaseModel):
    provider: dict[str, Any]


class EncryptRecordRequest(BaseModel):
    record_id: str = "rec_001"


class EncryptRecordResponse(BaseModel):
    record: dict[str, Any]


class AccessRequest(BaseModel):
    record_id: str = Field(min_length=1)
    provider_id: str = Field(min_length=1)
    purpose: str = Field(min_length=1)
    zkp_proof: dict[str, Any]
    zkp_public_signals: list[str] = Field(min_length=1)


class AccessResponse(BaseModel):
    decision: str
    record_id: str
    reason: str
    audit_event_id: str
    release_id: str | None = None
    encrypted_record: dict[str, Any] | None = None
    wrapped_dek: dict[str, Any] | None = None
    provenance_manifest: dict[str, Any] | None = None
    provenance_signature_b64: str | None = None


class AuditVerifyResponse(BaseModel):
    valid: bool
    entries_checked: int | None = None
    last_hash: str | None = None
    error: str | None = None


class AuditListResponse(BaseModel):
    entries: list[dict[str, Any]]
