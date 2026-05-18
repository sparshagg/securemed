from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from securemed.api.routes import get_store
from securemed.main import app
from securemed.services.access_gateway import (
    DEFAULT_PROVIDER_ID,
    DEFAULT_PURPOSE,
    DEFAULT_RECORD_ID,
    bootstrap_demo,
    create_demo_consent,
    decrypt_as_demo_provider,
    generate_demo_proof,
    request_access,
    revoke_credential,
)
from securemed.storage.json_state import DemoPaths, DemoStore
from securemed.zkp.credential import ZkpVerificationError, verify_credential_proof


def _ensure_zkp_artifacts() -> None:
    if not Path("circuits/build/verification_key.json").exists():
        if shutil.which("circom") is None:
            pytest.skip("circom is not installed; ZKP tests require circom toolchain")
        subprocess.run(["python3", "scripts/setup_zkp.py"], check=True)


def _store(tmp_path: Path) -> DemoStore:
    return DemoStore(DemoPaths(data_dir=tmp_path / "data"))


def test_valid_zkp_proof_verifies(tmp_path: Path) -> None:
    _ensure_zkp_artifacts()
    store = _store(tmp_path)
    setup = bootstrap_demo(store)
    proof = generate_demo_proof(store)

    verify_credential_proof(
        proof=proof["proof"],
        public_signals=proof["public_signals"],
        credential_commitment_value=setup["provider"]["credential_commitment"],
        required_role=setup["provider"]["role_code"],
        current_day=setup["zkp_input_hint"]["current_day"],
    )


def test_invalid_zkp_public_signal_is_rejected(tmp_path: Path) -> None:
    _ensure_zkp_artifacts()
    store = _store(tmp_path)
    setup = bootstrap_demo(store)
    proof = generate_demo_proof(store)
    public_signals = list(proof["public_signals"])
    public_signals[1] = "999"

    try:
        verify_credential_proof(
            proof=proof["proof"],
            public_signals=public_signals,
            credential_commitment_value=setup["provider"]["credential_commitment"],
            required_role=setup["provider"]["role_code"],
            current_day=setup["zkp_input_hint"]["current_day"],
        )
    except ZkpVerificationError:
        return
    raise AssertionError("invalid ZKP public signal was accepted")


def test_full_access_grant_decrypts_and_audits(tmp_path: Path) -> None:
    _ensure_zkp_artifacts()
    store = _store(tmp_path)
    bootstrap_demo(store)
    proof = generate_demo_proof(store)

    decision = request_access(
        store,
        record_id=DEFAULT_RECORD_ID,
        provider_id=DEFAULT_PROVIDER_ID,
        purpose=DEFAULT_PURPOSE,
        zkp_proof=proof["proof"],
        zkp_public_signals=proof["public_signals"],
    )
    decrypted = decrypt_as_demo_provider(
        store,
        provider_id=DEFAULT_PROVIDER_ID,
        access_decision=decision,
    )

    assert decision.decision == "ACCESS_GRANTED"
    assert decision.wrapped_dek is not None
    assert decrypted["resourceType"] == "Bundle"


def test_revoked_credential_denies_without_dek(tmp_path: Path) -> None:
    _ensure_zkp_artifacts()
    store = _store(tmp_path)
    setup = bootstrap_demo(store)
    proof = generate_demo_proof(store)
    revoke_credential(
        store, setup["provider"]["credential_commitment"], "test_revocation"
    )

    decision = request_access(
        store,
        record_id=DEFAULT_RECORD_ID,
        provider_id=DEFAULT_PROVIDER_ID,
        purpose=DEFAULT_PURPOSE,
        zkp_proof=proof["proof"],
        zkp_public_signals=proof["public_signals"],
    )

    assert decision.decision == "ACCESS_DENIED"
    assert decision.wrapped_dek is None
    assert decision.reason == "credential_revoked"


def test_consent_denied_does_not_release_dek(tmp_path: Path) -> None:
    _ensure_zkp_artifacts()
    store = _store(tmp_path)
    bootstrap_demo(store)
    create_demo_consent(store, decision="deny")
    proof = generate_demo_proof(store)

    decision = request_access(
        store,
        record_id=DEFAULT_RECORD_ID,
        provider_id=DEFAULT_PROVIDER_ID,
        purpose=DEFAULT_PURPOSE,
        zkp_proof=proof["proof"],
        zkp_public_signals=proof["public_signals"],
    )

    assert decision.decision == "ACCESS_DENIED"
    assert decision.wrapped_dek is None
    assert decision.reason == "consent_denied"


def test_api_grant_and_audit_verify(tmp_path: Path) -> None:
    _ensure_zkp_artifacts()
    store = _store(tmp_path)
    app.dependency_overrides[get_store] = lambda: store
    client = TestClient(app)
    try:
        setup_response = client.post("/setup/demo-data")
        assert setup_response.status_code == 200
        setup = setup_response.json()
        assert setup["zkp_ready"] is True

        access_response = client.post(
            "/access/request",
            json={
                "record_id": setup["record_id"],
                "provider_id": setup["provider_id"],
                "purpose": setup["purpose"],
                "zkp_proof": setup["demo_proof"]["proof"],
                "zkp_public_signals": setup["demo_proof"]["public_signals"],
            },
        )
        assert access_response.status_code == 200
        assert access_response.json()["decision"] == "ACCESS_GRANTED"

        audit_response = client.post("/audit/verify")
        assert audit_response.status_code == 200
        assert audit_response.json()["valid"] is True
    finally:
        app.dependency_overrides.clear()
