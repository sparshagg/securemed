# PLAN.md — Active Task Plan

This file tracks what has been done, what is currently being done, and what will be done next. Keep it short but accurate.

Legend:

```text
[ ] Pending
[~] In progress
[x] Complete
[!] Blocked
```

## Current Sprint: Bootstrap and First Working Crypto Slice

### Done

- [x] Repository initialized.
- [x] Core documentation created.
- [x] `.codex` skills/workflows created.
- [x] Created Python package skeleton.
- [x] Added dependency configuration.
- [x] Added fake sample EMR JSON.
- [x] Implemented AES-256-GCM utility.
- [x] Implemented ECDSA P-256 provenance utility.
- [x] Implemented hash-chained JSONL audit log.
- [x] Added crypto and audit success tests.
- [x] Added tamper-failure tests.
- [x] Ran pytest and ruff checks.
- [x] Updated README and security/testing docs with exact commands.
- [x] Committed first backend crypto/audit slice.
- [x] Checked Git remote; no remote is configured, so push was skipped.

### Doing

- [~] Ready to start X25519/HKDF/AES-GCM DEK wrapping next.

### Next

- [ ] Implement X25519/HKDF/AES-GCM DEK wrapping.
- [ ] Add key wrapping success and wrong-provider-key tests.
- [ ] Add audit verification command.

## Backlog

### Core Crypto

- [ ] Implement SHA-256 hashing utilities.
- [ ] Implement record manifest canonicalisation.
- [ ] Implement ECDSA provenance signing.
- [ ] Implement ECDSA provenance verification.
- [ ] Implement X25519/HKDF/AES-GCM DEK wrapping.
- [ ] Add RSA-OAEP compatibility only if core scope is complete.

### ZKP

- [ ] Create minimal credential circuit.
- [ ] Add valid credential sample input.
- [ ] Add invalid credential sample input.
- [ ] Add snarkjs compile/setup/prove/verify scripts.
- [ ] Add FastAPI proof verification wrapper.

### Access Gateway

- [ ] Implement provider registration.
- [ ] Implement consent state.
- [ ] Implement revocation state.
- [ ] Implement access request decision flow.
- [ ] Implement response payload containing encrypted record, wrapped DEK, and signed manifest.

### Audit

- [ ] Implement append-only audit event model.
- [ ] Implement audit hash chain.
- [ ] Implement audit verification command.
- [ ] Add audit tampering test.

### Docs and Demo

- [ ] Write API docs.
- [ ] Write demo script.
- [ ] Write prototype testing guide.
- [ ] Record final run instructions.
- [ ] Add explanation of limitations and future scope.

## Blockers / Questions

- [ ] Confirm whether the team wants SQLite or JSON files for first implementation.
- [ ] Confirm whether a frontend is required by the instructor or whether FastAPI Swagger is enough.
- [ ] Confirm whether snarkjs/Circom installation must be included in the demo or can be preinstalled.
