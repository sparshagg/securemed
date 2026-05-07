"""Generate a demo credential proof using local snarkjs artifacts."""

from __future__ import annotations

import argparse
import json
import secrets
import subprocess
from pathlib import Path

from securemed.zkp.credential import (
    credential_commitment,
    current_day_number,
    write_credential_input,
)

ROOT = Path(__file__).resolve().parents[1]
BUILD_DIR = ROOT / "circuits" / "build"
SNARKJS = ROOT / "node_modules" / ".bin" / "snarkjs"


def run(command: list[str]) -> None:
    subprocess.run(command, cwd=ROOT, check=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--credential-secret", type=int)
    parser.add_argument("--role-code", type=int, default=7)
    parser.add_argument("--required-role", type=int, default=7)
    parser.add_argument("--expiry-day", type=int, default=current_day_number() + 365)
    parser.add_argument("--salt", type=int)
    parser.add_argument("--out-dir", type=Path, default=Path("data/zkp"))
    args = parser.parse_args()
    credential_secret = args.credential_secret or secrets.randbelow(2**128)
    salt = args.salt or secrets.randbelow(2**128)

    commitment = credential_commitment(
        credential_secret=credential_secret,
        role_code=args.role_code,
        expiry_day=args.expiry_day,
        salt=salt,
    )
    out_dir = ROOT / args.out_dir
    snarkjs = str(SNARKJS) if SNARKJS.exists() else "snarkjs"
    out_dir.mkdir(parents=True, exist_ok=True)
    input_path = out_dir / "credential_input.json"
    witness_path = out_dir / "credential_witness.wtns"
    proof_path = out_dir / "proof.json"
    public_path = out_dir / "public.json"

    payload = write_credential_input(
        input_path,
        credential_secret=credential_secret,
        role_code=args.role_code,
        expiry_day=args.expiry_day,
        salt=salt,
        credential_commitment_value=commitment,
        required_role=args.required_role,
        current_day=current_day_number(),
    )
    run(
        [
            "node",
            str(BUILD_DIR / "credential_eligibility_js" / "generate_witness.js"),
            str(
                BUILD_DIR / "credential_eligibility_js" / "credential_eligibility.wasm"
            ),
            str(input_path),
            str(witness_path),
        ]
    )
    run(
        [
            snarkjs,
            "groth16",
            "prove",
            str(BUILD_DIR / "credential_eligibility_final.zkey"),
            str(witness_path),
            str(proof_path),
            str(public_path),
        ]
    )
    print(
        json.dumps(
            {
                "credential_commitment": commitment,
                "proof_path": str(proof_path),
                "public_path": str(public_path),
                "input": payload,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
