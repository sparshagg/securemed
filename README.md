# SecureMed Prototype

SecureMed is an academic cryptography prototype for **secure medical record sharing using hybrid encryption and zero-knowledge proofs**.

It demonstrates the core workflow required by the course report:

1. Encrypt a fake medical record.
2. Sign the record provenance.
3. Verify provider eligibility using a zero-knowledge proof.
4. Release the record key only after proof, consent, and revocation checks.
5. Decrypt the record as the authorised provider.
6. Record all access attempts in a tamper-evident audit log.

This repository must use **fake medical data only**. It is not production medical software.

## Prototype Scope

| Requirement | Prototype implementation |
|---|---|
| EMR confidentiality | AES-256-GCM |
| Provenance/authenticity | ECDSA P-256 signatures |
| Key release | X25519 + HKDF-SHA256 + AES-GCM wrapping |
| Provider eligibility privacy | Circom/snarkjs ZKP |
| Consent/revocation | Local JSON/SQLite checks |
| Auditability | Hash-chained JSONL audit log |
| API demo | FastAPI |

## Expected Demo Flow

```text
Fake EMR created
  → EMR encrypted with AES-256-GCM
  → provenance manifest signed
  → provider generates ZKP credential proof
  → gateway verifies proof + consent + revocation
  → gateway wraps DEK to provider
  → provider decrypts EMR
  → audit log records grant/deny event
```

## Requirements

Install:

- Python 3.11+
- Node.js 20+
- npm
- Circom
- snarkjs
- Git

Python dependencies are declared in `pyproject.toml`.
Node dependencies are declared in `package.json`.

## Quick Start

Current setup:

```bash
cd /Users/sparshaggarwal/Projekts/securemed

python -m venv .venv
source .venv/bin/activate

pip install -e ".[dev]"
npm install

cargo install --git https://github.com/iden3/circom.git --locked
```

Build local ZKP artifacts and run the full demo:

```bash
python scripts/setup_zkp.py
python scripts/run_full_demo.py
pytest
ruff check .
ruff format --check .
```

Run the API and tiny demo UI:

```bash
fastapi dev
```

Open:

```text
http://127.0.0.1:8000/demo
http://127.0.0.1:8000/docs
```

## Main Commands

Current commands:

```bash
python scripts/setup_zkp.py
python scripts/bootstrap_demo.py
python scripts/run_full_demo.py
python scripts/verify_audit_log.py
pytest
ruff check .
ruff format --check .
fastapi dev
```

## API Endpoints

| Endpoint | Purpose |
|---|---|
| `POST /setup/demo-data` | Create fake keys, fake provider, fake consent, and fake EMR |
| `POST /records/encrypt` | Encrypt and sign a fake EMR |
| `POST /provider/register` | Register provider public key and credential commitment |
| `POST /access/request` | Request access to an encrypted record |
| `GET /audit` | View audit log entries |
| `POST /audit/verify` | Verify audit hash chain |

Endpoint details belong in `docs/API.md`.

Status: API endpoints are implemented for the local prototype.

## Test Scenarios

The repository should prove these cases:

Implemented now:

1. AES-GCM encryption/decryption roundtrip.
2. Fresh AES-GCM nonce for repeated encryption with the same DEK.
3. Tampered ciphertext fails AES-GCM authentication.
4. Tampered AAD fails AES-GCM authentication.
5. Valid ECDSA P-256 provenance signature verifies.
6. Tampered provenance fails signature verification.
7. Wrong signing public key fails signature verification.
8. Valid audit log chain verifies.
9. Modified, deleted, and reordered audit log entries are detected.
10. X25519/HKDF/AES-GCM DEK wrapping succeeds for the intended provider.
11. Wrong provider key, tampered wrapped DEK, and tampered release AAD fail.
12. Valid ZKP proof is accepted.
13. Invalid ZKP public signal is rejected.
14. Revoked credential is denied.
15. Consent-denied request does not release the DEK.
16. FastAPI grant flow records an audit event and verifies the chain.

## Repository Documents

| File | Purpose |
|---|---|
| `AGENTS.md` | Source of truth for AI agents |
| `ROADMAP.md` | Milestone roadmap |
| `PLAN.md` | Current checkbox task plan |
| `SECURITY.md` | Threat model and secure coding rules |
| `DATABASE.md` | Storage/schema design |
| `LEARNINGS.md` | Lessons discovered during development |
| `.codex/skills/` | Reusable agent skills |
| `.codex/workflows/` | Repeatable implementation workflows |

## Security Warning

Do not use real patient data, real credentials, production keys, or production healthcare systems in this prototype.

Generated private keys, ZKP proving artifacts, `.env`, and local databases must not be committed.
