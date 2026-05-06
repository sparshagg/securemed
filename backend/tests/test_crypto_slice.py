from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest
from securemed.crypto.aes_gcm import (
    DecryptionFailedError,
    EncryptedPayload,
    decrypt,
    encrypt,
)
from securemed.crypto.canonical import canonical_json_bytes
from securemed.crypto.hashing import sha256_json_hex
from securemed.crypto.provenance import (
    ProvenanceVerificationError,
    generate_signing_key,
    sign_manifest,
    verify_manifest_signature,
)
from securemed.storage.audit import (
    AuditLogVerificationError,
    append_audit_event,
    read_audit_entries,
    verify_audit_log,
)


def _sample_record() -> dict[str, object]:
    sample_path = Path("sample_data/fake_emr_record.json")
    return json.loads(sample_path.read_text(encoding="utf-8"))


def _sample_aad(record: dict[str, object]) -> bytes:
    aad = {
        "record_id": "rec_001",
        "record_hash": sha256_json_hex(record),
        "record_version": 1,
        "origin": "securemed-demo-hospital",
    }
    return canonical_json_bytes(aad)


def test_aes_gcm_encrypt_decrypt_roundtrip() -> None:
    record = _sample_record()
    plaintext = canonical_json_bytes(record)
    aad = _sample_aad(record)

    dek, payload = encrypt(plaintext, aad)

    assert len(dek) == 32
    assert len(payload.nonce) == 12
    assert decrypt(payload, aad, dek) == plaintext


def test_aes_gcm_uses_fresh_nonce_for_same_key() -> None:
    record = _sample_record()
    plaintext = canonical_json_bytes(record)
    aad = _sample_aad(record)
    dek, first_payload = encrypt(plaintext, aad)

    _, second_payload = encrypt(plaintext, aad, dek=dek)

    assert first_payload.nonce != second_payload.nonce


def test_aes_gcm_rejects_tampered_ciphertext() -> None:
    record = _sample_record()
    plaintext = canonical_json_bytes(record)
    aad = _sample_aad(record)
    dek, payload = encrypt(plaintext, aad)
    tampered_ciphertext = bytearray(payload.ciphertext)
    tampered_ciphertext[0] ^= 1

    with pytest.raises(DecryptionFailedError):
        decrypt(
            EncryptedPayload(
                nonce=payload.nonce,
                ciphertext=bytes(tampered_ciphertext),
            ),
            aad,
            dek,
        )


def test_aes_gcm_rejects_tampered_aad() -> None:
    record = _sample_record()
    plaintext = canonical_json_bytes(record)
    aad = _sample_aad(record)
    dek, payload = encrypt(plaintext, aad)

    with pytest.raises(DecryptionFailedError):
        decrypt(payload, b'{"record_id":"rec_999"}', dek)


def test_provenance_signature_verifies_manifest() -> None:
    record = _sample_record()
    signing_key = generate_signing_key()
    manifest = {
        "record_id": "rec_001",
        "record_hash": sha256_json_hex(record),
        "record_version": 1,
        "origin": "securemed-demo-hospital",
        "alg": "ECDSA-P256-SHA256",
    }

    signature = sign_manifest(signing_key, manifest)

    verify_manifest_signature(signing_key.public_key(), manifest, signature)


def test_provenance_rejects_modified_manifest() -> None:
    record = _sample_record()
    signing_key = generate_signing_key()
    manifest = {
        "record_id": "rec_001",
        "record_hash": sha256_json_hex(record),
        "record_version": 1,
        "origin": "securemed-demo-hospital",
        "alg": "ECDSA-P256-SHA256",
    }
    signature = sign_manifest(signing_key, manifest)
    tampered_manifest = copy.deepcopy(manifest)
    tampered_manifest["origin"] = "attacker-hospital"

    with pytest.raises(ProvenanceVerificationError):
        verify_manifest_signature(
            signing_key.public_key(), tampered_manifest, signature
        )


def test_provenance_rejects_wrong_public_key() -> None:
    record = _sample_record()
    signing_key = generate_signing_key()
    wrong_key = generate_signing_key()
    manifest = {
        "record_id": "rec_001",
        "record_hash": sha256_json_hex(record),
        "record_version": 1,
        "origin": "securemed-demo-hospital",
        "alg": "ECDSA-P256-SHA256",
    }
    signature = sign_manifest(signing_key, manifest)

    with pytest.raises(ProvenanceVerificationError):
        verify_manifest_signature(wrong_key.public_key(), manifest, signature)


def test_audit_log_verifies_valid_chain(tmp_path: Path) -> None:
    audit_path = tmp_path / "audit.jsonl"
    append_audit_event(
        audit_path,
        record_id="rec_001",
        provider_id="provider_001",
        credential_commitment="commitment_001",
        action="ACCESS_GRANTED",
        reason="valid_demo_request",
        release_id="rel_001",
    )
    append_audit_event(
        audit_path,
        record_id="rec_001",
        provider_id="provider_002",
        credential_commitment="commitment_002",
        action="ACCESS_DENIED",
        reason="credential_revoked",
    )

    result = verify_audit_log(audit_path)

    assert result.valid is True
    assert result.entries_checked == 2
    assert len(result.last_hash) == 64


def test_audit_log_detects_modified_entry(tmp_path: Path) -> None:
    audit_path = tmp_path / "audit.jsonl"
    append_audit_event(
        audit_path,
        record_id="rec_001",
        provider_id="provider_001",
        credential_commitment="commitment_001",
        action="ACCESS_DENIED",
        reason="consent_denied",
    )
    entries = read_audit_entries(audit_path)
    entries[0]["reason"] = "valid_demo_request"
    audit_path.write_text(
        "\n".join(json.dumps(entry, sort_keys=True) for entry in entries) + "\n",
        encoding="utf-8",
    )

    with pytest.raises(AuditLogVerificationError):
        verify_audit_log(audit_path)


def test_audit_log_detects_deleted_entry(tmp_path: Path) -> None:
    audit_path = tmp_path / "audit.jsonl"
    append_audit_event(
        audit_path,
        record_id="rec_001",
        provider_id="provider_001",
        credential_commitment="commitment_001",
        action="ACCESS_GRANTED",
        reason="valid_demo_request",
        release_id="rel_001",
    )
    append_audit_event(
        audit_path,
        record_id="rec_002",
        provider_id="provider_001",
        credential_commitment="commitment_001",
        action="ACCESS_DENIED",
        reason="consent_denied",
    )
    entries = read_audit_entries(audit_path)
    audit_path.write_text(
        json.dumps(entries[1], sort_keys=True) + "\n", encoding="utf-8"
    )

    with pytest.raises(AuditLogVerificationError):
        verify_audit_log(audit_path)


def test_audit_log_detects_reordered_entries(tmp_path: Path) -> None:
    audit_path = tmp_path / "audit.jsonl"
    append_audit_event(
        audit_path,
        record_id="rec_001",
        provider_id="provider_001",
        credential_commitment="commitment_001",
        action="ACCESS_GRANTED",
        reason="valid_demo_request",
        release_id="rel_001",
    )
    append_audit_event(
        audit_path,
        record_id="rec_002",
        provider_id="provider_002",
        credential_commitment="commitment_002",
        action="ACCESS_DENIED",
        reason="credential_revoked",
    )
    entries = read_audit_entries(audit_path)
    audit_path.write_text(
        "\n".join(json.dumps(entry, sort_keys=True) for entry in reversed(entries))
        + "\n",
        encoding="utf-8",
    )

    with pytest.raises(AuditLogVerificationError):
        verify_audit_log(audit_path)


def test_audit_append_rejects_existing_tampered_chain(tmp_path: Path) -> None:
    audit_path = tmp_path / "audit.jsonl"
    append_audit_event(
        audit_path,
        record_id="rec_001",
        provider_id="provider_001",
        credential_commitment="commitment_001",
        action="ACCESS_DENIED",
        reason="consent_denied",
    )
    entries = read_audit_entries(audit_path)
    entries[0]["action"] = "ACCESS_GRANTED"
    audit_path.write_text(
        json.dumps(entries[0], sort_keys=True) + "\n", encoding="utf-8"
    )

    with pytest.raises(AuditLogVerificationError):
        append_audit_event(
            audit_path,
            record_id="rec_002",
            provider_id="provider_002",
            credential_commitment="commitment_002",
            action="ACCESS_DENIED",
            reason="credential_revoked",
        )
