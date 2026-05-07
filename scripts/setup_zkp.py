"""Compile and set up the local SecureMed Groth16 credential circuit."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILD_DIR = ROOT / "circuits" / "build"
CIRCUIT = ROOT / "circuits" / "credential_eligibility.circom"
SNARKJS = ROOT / "node_modules" / ".bin" / "snarkjs"


def run(command: list[str]) -> None:
    subprocess.run(command, cwd=ROOT, check=True)


def main() -> None:
    if shutil.which("circom") is None:
        raise SystemExit("circom is not installed; install it with Cargo before setup")
    if not SNARKJS.exists() and shutil.which("snarkjs") is None:
        raise SystemExit("snarkjs is not installed; run npm install first")
    snarkjs = str(SNARKJS) if SNARKJS.exists() else "snarkjs"

    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    run(["circom", str(CIRCUIT), "--r1cs", "--wasm", "--sym", "-o", str(BUILD_DIR)])
    run(
        [
            snarkjs,
            "powersoftau",
            "new",
            "bn128",
            "12",
            str(BUILD_DIR / "pot12_0000.ptau"),
            "-v",
        ]
    )
    run(
        [
            snarkjs,
            "powersoftau",
            "contribute",
            str(BUILD_DIR / "pot12_0000.ptau"),
            str(BUILD_DIR / "pot12_0001.ptau"),
            "--name=SecureMed demo contribution",
            "-v",
            "-e=securemed-local-demo",
        ]
    )
    run(
        [
            snarkjs,
            "powersoftau",
            "prepare",
            "phase2",
            str(BUILD_DIR / "pot12_0001.ptau"),
            str(BUILD_DIR / "pot12_final.ptau"),
            "-v",
        ]
    )
    run(
        [
            snarkjs,
            "groth16",
            "setup",
            str(BUILD_DIR / "credential_eligibility.r1cs"),
            str(BUILD_DIR / "pot12_final.ptau"),
            str(BUILD_DIR / "credential_eligibility_0000.zkey"),
        ]
    )
    run(
        [
            snarkjs,
            "zkey",
            "contribute",
            str(BUILD_DIR / "credential_eligibility_0000.zkey"),
            str(BUILD_DIR / "credential_eligibility_final.zkey"),
            "--name=SecureMed local zkey contribution",
            "-v",
            "-e=securemed-local-zkey",
        ]
    )
    run(
        [
            snarkjs,
            "zkey",
            "export",
            "verificationkey",
            str(BUILD_DIR / "credential_eligibility_final.zkey"),
            str(BUILD_DIR / "verification_key.json"),
        ]
    )
    print(f"ZKP artifacts created under {BUILD_DIR}")


if __name__ == "__main__":
    main()
