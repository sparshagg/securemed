"""snarkjs-backed credential proof helpers."""

from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


class ZkpVerificationError(ValueError):
    """Raised when credential proof verification fails closed."""


def snarkjs_command() -> str:
    """Return the project-local snarkjs command when available."""
    local = Path("node_modules") / ".bin" / "snarkjs"
    if local.exists():
        return str(local)
    found = shutil.which("snarkjs")
    if found is None:
        raise ZkpVerificationError("missing ZKP tool: snarkjs")
    return found


def circom_command() -> str:
    """Return the installed circom command."""
    found = shutil.which("circom")
    if found is None:
        raise ZkpVerificationError("missing ZKP tool: circom")
    return found


@dataclass(frozen=True)
class ZkpArtifacts:
    build_dir: Path = Path("circuits/build")

    @property
    def verification_key_path(self) -> Path:
        return self.build_dir / "verification_key.json"

    @property
    def wasm_path(self) -> Path:
        return (
            self.build_dir / "credential_eligibility_js" / "credential_eligibility.wasm"
        )

    @property
    def witness_generator_path(self) -> Path:
        return self.build_dir / "credential_eligibility_js" / "generate_witness.js"

    @property
    def zkey_path(self) -> Path:
        return self.build_dir / "credential_eligibility_final.zkey"


def current_day_number(now: datetime | None = None) -> int:
    """Return UTC day count used by the ZKP expiry predicate."""
    current = now or datetime.now(UTC)
    return int(current.timestamp() // 86_400)


def ensure_zkp_tools_available() -> None:
    """Fail if the real local ZKP toolchain is unavailable."""
    missing = [tool for tool in ("node",) if shutil.which(tool) is None]
    if shutil.which("circom") is None:
        missing.append("circom")
    if (
        not (Path("node_modules") / ".bin" / "snarkjs").exists()
        and shutil.which("snarkjs") is None
    ):
        missing.append("snarkjs")
    if missing:
        raise ZkpVerificationError(f"missing ZKP tool(s): {', '.join(missing)}")


def credential_commitment(
    *,
    credential_secret: int,
    role_code: int,
    expiry_day: int,
    salt: int,
) -> str:
    """Compute the Poseidon credential commitment using circomlibjs."""
    result = subprocess.run(
        [
            "node",
            "scripts/zkp/credential_commitment.mjs",
            str(credential_secret),
            str(role_code),
            str(expiry_day),
            str(salt),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def write_credential_input(
    path: Path,
    *,
    credential_secret: int,
    role_code: int,
    expiry_day: int,
    salt: int,
    credential_commitment_value: str,
    required_role: int,
    current_day: int,
) -> dict[str, str]:
    """Write a snarkjs input JSON file for the credential circuit."""
    payload = {
        "credentialSecret": str(credential_secret),
        "roleCode": str(role_code),
        "expiryDay": str(expiry_day),
        "salt": str(salt),
        "credentialCommitment": str(credential_commitment_value),
        "requiredRole": str(required_role),
        "currentDay": str(current_day),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return payload


def verify_credential_proof(
    *,
    proof: dict[str, Any],
    public_signals: list[str],
    credential_commitment_value: str,
    required_role: int,
    current_day: int,
    artifacts: ZkpArtifacts | None = None,
) -> None:
    """Verify a Groth16 proof and validate public signals against policy inputs."""
    ensure_zkp_tools_available()
    paths = artifacts or ZkpArtifacts()
    if not paths.verification_key_path.exists():
        raise ZkpVerificationError("missing ZKP verification key")
    if len(public_signals) < 4 or str(public_signals[0]) != "1":
        raise ZkpVerificationError("ZKP eligibility output is not true")
    expected_public_inputs = [
        str(credential_commitment_value),
        str(required_role),
        str(current_day),
    ]
    actual_public_inputs = [str(value) for value in public_signals[1:4]]
    if actual_public_inputs != expected_public_inputs:
        raise ZkpVerificationError("ZKP public signals do not match access request")

    with tempfile.TemporaryDirectory(prefix="securemed_zkp_verify_") as temp_dir:
        temp_path = Path(temp_dir)
        public_path = temp_path / "public.json"
        proof_path = temp_path / "proof.json"
        public_path.write_text(json.dumps(public_signals), encoding="utf-8")
        proof_path.write_text(json.dumps(proof), encoding="utf-8")
        result = subprocess.run(
            [
                snarkjs_command(),
                "groth16",
                "verify",
                str(paths.verification_key_path),
                str(public_path),
                str(proof_path),
            ],
            capture_output=True,
            text=True,
        )
    if result.returncode != 0:
        raise ZkpVerificationError(result.stderr.strip() or result.stdout.strip())


def verify_credential_proof_files(
    *,
    proof_path: Path,
    public_path: Path,
    credential_commitment_value: str,
    required_role: int,
    current_day: int,
    artifacts: ZkpArtifacts | None = None,
) -> None:
    """Verify a proof from snarkjs JSON files."""
    proof = json.loads(proof_path.read_text(encoding="utf-8"))
    public_signals = json.loads(public_path.read_text(encoding="utf-8"))
    verify_credential_proof(
        proof=proof,
        public_signals=[str(value) for value in public_signals],
        credential_commitment_value=credential_commitment_value,
        required_role=required_role,
        current_day=current_day,
        artifacts=artifacts,
    )
