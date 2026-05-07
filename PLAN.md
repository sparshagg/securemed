# PLAN.md — Active Task Plan

This file tracks what has been done, what is currently being done, and what will be done next. Keep it short but accurate.

Legend:

```text
[ ] Pending
[~] In progress
[x] Complete
[!] Blocked
```

## Current Sprint: Full Demo Flow

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
- [x] Merged FastAPI skill cleanup into `main`.
- [x] Added FastAPI, ZKP, and demo dependencies.
- [x] Implemented X25519/HKDF/AES-GCM DEK wrapping.
- [x] Implemented JSON state, consent, revocation, and access gateway checks.
- [x] Added real Circom/snarkjs credential proof tooling.
- [x] Added FastAPI API endpoints and tiny demo UI.
- [x] Added demo and audit verification scripts.
- [x] Added unit and integration tests for grant/deny flows.
- [x] Ran pytest and ruff checks for full demo flow.
- [x] Updated final docs and quality gates.
- [x] Ran final secret/artifact scan.

### Next

- [ ] Commit and push `feat/full-demo-flow`.

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

- [x] Use JSON/JSONL storage for the full local demo.
- [x] Add a tiny FastAPI-served demo UI after the API works.
- [x] Use real Circom/snarkjs tooling; stop on concrete install/runtime blockers instead of mocking ZKP.
