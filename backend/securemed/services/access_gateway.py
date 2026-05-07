"""SecureMed demo service layer for record access decisions."""

from __future__ import annotations

import json
import secrets
import subprocess
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any
from uuid import uuid4

from securemed.crypto.aes_gcm import EncryptedPayload, decrypt, encrypt
from securemed.crypto.canonical import canonical_json_bytes
from securemed.crypto.encoding import b64decode, b64encode
from securemed.crypto.hashing import sha256_json_hex
from securemed.crypto.key_wrapping import (
    generate_x25519_key_pair,
    release_aad,
    unwrap_dek_from_gateway,
    wrap_dek_for_provider,
    wrapped_dek_from_json,
    wrapped_dek_to_json,
)
from securemed.crypto.provenance import (
    generate_signing_key,
    load_public_key_pem,
    public_key_pem,
    sign_manifest,
    verify_manifest_signature,
)
from securemed.storage.audit import (
    AuditLogVerificationError,
    append_audit_event,
    read_audit_entries,
    verify_audit_log,
)
from securemed.storage.json_state import DemoPaths, DemoStore, StateNotFoundError
from securemed.zkp.credential import (
    ZkpArtifacts,
    ZkpVerificationError,
    credential_commitment,
    current_day_number,
    snarkjs_command,
    verify_credential_proof,
    write_credential_input,
)

DEFAULT_RECORD_ID = "rec_001"
DEFAULT_PROVIDER_ID = "provider_001"
DEFAULT_PURPOSE = "treatment"
DEFAULT_ROLE_CODE = 7


@dataclass(frozen=True)
class AccessDecision:
    decision: str
    record_id: str
    reason: str
    audit_event_id: str
    release_id: str | None = None
    encrypted_record: dict[str, Any] | None = None
    wrapped_dek: dict[str, Any] | None = None
    provenance_manifest: dict[str, Any] | None = None
    provenance_signature_b64: str | None = None


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()


def _load_sample_record() -> dict[str, Any]:
    path = Path("sample_data/fake_emr_record.json")
    return json.loads(path.read_text(encoding="utf-8"))


def create_signed_encrypted_record(
    store: DemoStore,
    *,
    record_id: str = DEFAULT_RECORD_ID,
) -> dict[str, Any]:
    """Encrypt the fake EMR and sign its provenance manifest."""
    sample_record = _load_sample_record()
    aad = {
        "record_id": record_id,
        "record_hash": sha256_json_hex(sample_record),
        "record_version": "1",
        "origin": "securemed-demo-hospital",
    }
    dek, encrypted_payload = encrypt(
        canonical_json_bytes(sample_record), canonical_json_bytes(aad)
    )
    signing_key = generate_signing_key()
    manifest = {
        "record_id": record_id,
        "record_hash": sha256_json_hex(sample_record),
        "encrypted_payload_hash": sha256_json_hex(encrypted_payload.to_json()),
        "record_version": "1",
        "origin": "securemed-demo-hospital",
        "alg": "ECDSA-P256-SHA256",
        "created_at": _now_iso(),
        "signing_public_key_pem": public_key_pem(signing_key.public_key()),
    }
    signature = sign_manifest(signing_key, manifest)
    verify_manifest_signature(signing_key.public_key(), manifest, signature)
    record = {
        "record_id": record_id,
        "patient_pseudonym": "patient_pseudo_001",
        "encrypted_record": encrypted_payload.to_json(),
        "aad": aad,
        "provenance_manifest": manifest,
        "provenance_signature_b64": b64encode(signature),
        "created_at": _now_iso(),
    }
    store.save_record(record_id, record)
    store.save_record_key(record_id, b64encode(dek))
    return record


def register_demo_provider(
    store: DemoStore,
    *,
    provider_id: str = DEFAULT_PROVIDER_ID,
    role_code: int = DEFAULT_ROLE_CODE,
) -> dict[str, Any]:
    """Register a fake provider with public keys and a credential commitment."""
    key_pair = generate_x25519_key_pair()
    private = {
        "provider_id": provider_id,
        "x25519_private_key_b64": key_pair.private_b64(),
        "credential_secret": secrets.randbelow(2**128),
        "credential_salt": secrets.randbelow(2**128),
        "credential_expiry_day": current_day_number() + 365,
    }
    commitment = credential_commitment(
        credential_secret=private["credential_secret"],
        role_code=role_code,
        expiry_day=private["credential_expiry_day"],
        salt=private["credential_salt"],
    )
    provider = {
        "provider_id": provider_id,
        "provider_label": "Demo Doctor",
        "x25519_public_key_b64": key_pair.public_b64(),
        "credential_commitment": commitment,
        "role_code": role_code,
        "status": "active",
        "created_at": _now_iso(),
    }
    private["credential_commitment"] = commitment
    private["role_code"] = role_code
    store.save_provider(provider_id, provider)
    provider_private = store.read_provider_private()
    provider_private[provider_id] = private
    store.write_provider_private(provider_private)
    return provider


def create_demo_consent(
    store: DemoStore,
    *,
    record_id: str = DEFAULT_RECORD_ID,
    provider_id: str = DEFAULT_PROVIDER_ID,
    purpose: str = DEFAULT_PURPOSE,
    decision: str = "allow",
) -> dict[str, Any]:
    policy = {
        "consent_id": f"consent_{uuid4().hex}",
        "record_id": record_id,
        "provider_id": provider_id,
        "purpose": purpose,
        "decision": decision,
        "expires_at": (datetime.now(UTC) + timedelta(days=90)).isoformat(),
        "created_at": _now_iso(),
    }
    policies = [
        item
        for item in store.read_consent_policies()
        if not (
            item.get("record_id") == record_id
            and item.get("provider_id") == provider_id
            and item.get("purpose") == purpose
        )
    ]
    policies.append(policy)
    store.write_consent_policies(policies)
    return policy


def bootstrap_demo(store: DemoStore) -> dict[str, Any]:
    """Create fake record, provider, consent, and empty revocation state."""
    store.ensure_dirs()
    record = create_signed_encrypted_record(store)
    provider = register_demo_provider(store)
    consent = create_demo_consent(store)
    store.write_revoked_credentials([])
    return {
        "record": record,
        "provider": provider,
        "consent": consent,
        "zkp_input_hint": {
            "required_role": DEFAULT_ROLE_CODE,
            "current_day": current_day_number(),
        },
    }


def generate_demo_proof(
    store: DemoStore,
    *,
    provider_id: str = DEFAULT_PROVIDER_ID,
    required_role: int = DEFAULT_ROLE_CODE,
) -> dict[str, Any]:
    """Generate a real snarkjs proof for the registered demo provider."""
    private = dict(store.read_provider_private()[provider_id])
    artifacts = ZkpArtifacts()
    out_dir = store.paths.zkp_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    input_path = out_dir / "credential_input.json"
    witness_path = out_dir / "credential_witness.wtns"
    proof_path = out_dir / "proof.json"
    public_path = out_dir / "public.json"
    write_credential_input(
        input_path,
        credential_secret=int(private["credential_secret"]),
        role_code=int(private["role_code"]),
        expiry_day=int(private["credential_expiry_day"]),
        salt=int(private["credential_salt"]),
        credential_commitment_value=str(private["credential_commitment"]),
        required_role=required_role,
        current_day=current_day_number(),
    )
    subprocess.run(
        [
            "node",
            str(artifacts.witness_generator_path),
            str(artifacts.wasm_path),
            str(input_path),
            str(witness_path),
        ],
        check=True,
    )
    subprocess.run(
        [
            snarkjs_command(),
            "groth16",
            "prove",
            str(artifacts.zkey_path),
            str(witness_path),
            str(proof_path),
            str(public_path),
        ],
        check=True,
    )
    proof = json.loads(proof_path.read_text(encoding="utf-8"))
    public_signals = json.loads(public_path.read_text(encoding="utf-8"))
    return {
        "proof": proof,
        "public_signals": [str(value) for value in public_signals],
        "proof_path": str(proof_path),
        "public_path": str(public_path),
    }


def is_credential_revoked(store: DemoStore, credential_commitment_value: str) -> bool:
    return any(
        item.get("credential_commitment") == credential_commitment_value
        for item in store.read_revoked_credentials()
    )


def revoke_credential(
    store: DemoStore, credential_commitment_value: str, reason: str
) -> None:
    revoked = store.read_revoked_credentials()
    revoked.append(
        {
            "credential_commitment": credential_commitment_value,
            "reason": reason,
            "revoked_at": _now_iso(),
        }
    )
    store.write_revoked_credentials(revoked)


def consent_allows(
    store: DemoStore,
    *,
    record_id: str,
    provider_id: str,
    purpose: str,
) -> bool:
    now = datetime.now(UTC)
    for policy in store.read_consent_policies():
        if (
            policy.get("record_id") == record_id
            and policy.get("provider_id") == provider_id
            and policy.get("purpose") == purpose
        ):
            expires_at = datetime.fromisoformat(str(policy["expires_at"]))
            return policy.get("decision") == "allow" and expires_at > now
    return False


def _deny(
    store: DemoStore,
    *,
    record_id: str,
    provider_id: str,
    credential_commitment_value: str,
    reason: str,
) -> AccessDecision:
    event = append_audit_event(
        store.paths.audit_path,
        record_id=record_id,
        provider_id=provider_id,
        credential_commitment=credential_commitment_value,
        action="ACCESS_DENIED",
        reason=reason,
    )
    return AccessDecision(
        decision="ACCESS_DENIED",
        record_id=record_id,
        reason=reason,
        audit_event_id=str(event["event_id"]),
    )


def request_access(
    store: DemoStore,
    *,
    record_id: str,
    provider_id: str,
    purpose: str,
    zkp_proof: dict[str, Any],
    zkp_public_signals: list[str],
) -> AccessDecision:
    """Verify proof/policy and release a wrapped DEK only on success."""
    try:
        record = store.get_record(record_id)
        provider = store.get_provider(provider_id)
    except StateNotFoundError as exc:
        return _deny(
            store,
            record_id=record_id,
            provider_id=provider_id,
            credential_commitment_value="unknown",
            reason=str(exc),
        )

    commitment = str(provider["credential_commitment"])
    if provider.get("status") != "active":
        return _deny(
            store,
            record_id=record_id,
            provider_id=provider_id,
            credential_commitment_value=commitment,
            reason="provider_inactive",
        )

    try:
        verify_credential_proof(
            proof=zkp_proof,
            public_signals=zkp_public_signals,
            credential_commitment_value=commitment,
            required_role=int(provider["role_code"]),
            current_day=current_day_number(),
        )
    except ZkpVerificationError as exc:
        return _deny(
            store,
            record_id=record_id,
            provider_id=provider_id,
            credential_commitment_value=commitment,
            reason=f"invalid_zkp:{exc}",
        )

    if is_credential_revoked(store, commitment):
        return _deny(
            store,
            record_id=record_id,
            provider_id=provider_id,
            credential_commitment_value=commitment,
            reason="credential_revoked",
        )
    if not consent_allows(
        store,
        record_id=record_id,
        provider_id=provider_id,
        purpose=purpose,
    ):
        return _deny(
            store,
            record_id=record_id,
            provider_id=provider_id,
            credential_commitment_value=commitment,
            reason="consent_denied",
        )

    release_id = f"rel_{uuid4().hex}"
    aad = release_aad(
        record_id=record_id,
        provider_id=provider_id,
        credential_commitment=commitment,
        purpose=purpose,
        release_id=release_id,
    )
    wrapped_dek = wrap_dek_for_provider(
        dek=b64decode(store.get_record_key(record_id)),
        provider_public_key_b64=str(provider["x25519_public_key_b64"]),
        aad=aad,
    )
    event = append_audit_event(
        store.paths.audit_path,
        record_id=record_id,
        provider_id=provider_id,
        credential_commitment=commitment,
        action="ACCESS_GRANTED",
        reason="access_policy_satisfied",
        release_id=release_id,
    )
    return AccessDecision(
        decision="ACCESS_GRANTED",
        record_id=record_id,
        reason="access_policy_satisfied",
        audit_event_id=str(event["event_id"]),
        release_id=release_id,
        encrypted_record=dict(record["encrypted_record"]),
        wrapped_dek=wrapped_dek_to_json(wrapped_dek),
        provenance_manifest=dict(record["provenance_manifest"]),
        provenance_signature_b64=str(record["provenance_signature_b64"]),
    )


def decrypt_as_demo_provider(
    store: DemoStore,
    *,
    provider_id: str,
    access_decision: AccessDecision,
) -> dict[str, Any]:
    """Provider-side decrypt helper for local scripts, not gateway policy."""
    if (
        access_decision.decision != "ACCESS_GRANTED"
        or access_decision.wrapped_dek is None
    ):
        raise ValueError("access decision did not release a wrapped DEK")
    provider_private = store.read_provider_private()[provider_id]
    wrapped_dek = wrapped_dek_from_json(access_decision.wrapped_dek)
    dek = unwrap_dek_from_gateway(
        wrapped_dek=wrapped_dek,
        provider_private_key_b64=str(provider_private["x25519_private_key_b64"]),
        expected_aad=wrapped_dek.aad,
    )
    record = store.get_record(access_decision.record_id)
    payload_json = dict(record["encrypted_record"])
    plaintext = decrypt(
        EncryptedPayload(
            nonce=b64decode(str(payload_json["nonce_b64"])),
            ciphertext=b64decode(str(payload_json["ciphertext_b64"])),
        ),
        canonical_json_bytes(record["aad"]),
        dek,
    )
    manifest = dict(record["provenance_manifest"])
    verify_manifest_signature(
        load_public_key_pem(str(manifest["signing_public_key_pem"])),
        manifest,
        b64decode(str(record["provenance_signature_b64"])),
    )
    return json.loads(plaintext.decode("utf-8"))


def list_audit(store: DemoStore) -> list[dict[str, Any]]:
    return read_audit_entries(store.paths.audit_path)


def verify_audit(store: DemoStore) -> dict[str, Any]:
    try:
        result = verify_audit_log(store.paths.audit_path)
        return {
            "valid": result.valid,
            "entries_checked": result.entries_checked,
            "last_hash": result.last_hash,
        }
    except AuditLogVerificationError as exc:
        return {"valid": False, "error": str(exc)}


def store_for_data_dir(data_dir: Path | None = None) -> DemoStore:
    return DemoStore(DemoPaths(data_dir=data_dir or Path("data")))
