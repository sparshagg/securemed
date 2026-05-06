# ROADMAP.md — SecureMed Prototype Roadmap

This roadmap tracks milestone-level progress. Detailed active work belongs in `PLAN.md`.

Legend:

```text
[ ] Not started
[~] In progress
[x] Complete
[!] Blocked
```

## Milestone 0 — Repository Bootstrap

- [x] Create base repository structure.
- [x] Add AGENTS.md, README.md, ROADMAP.md, PLAN.md, SECURITY.md, DATABASE.md, LEARNINGS.md.
- [x] Add `.codex/skills` and `.codex/workflows`.
- [x] Add `.gitignore`.
- [x] Add initial Python project configuration.
- [x] Add initial test setup.

Exit criteria:
- Repository can install dependencies.
- `pytest` can run, even if only placeholder tests exist.
- All core docs exist.

## Milestone 1 — Core Cryptographic Objects

- [x] Add fake FHIR-like EMR sample.
- [x] Implement AES-256-GCM encrypt/decrypt utilities.
- [x] Implement SHA-256 hashing utilities.
- [x] Implement ECDSA P-256 signing and verification.
- [x] Add tests for roundtrip encryption.
- [x] Add negative tests for tampered ciphertext.
- [x] Add negative tests for invalid signatures.

Exit criteria:
- A fake record can be encrypted, signed, decrypted, and verified.
- Tampering is detected.

## Milestone 2 — Audit Chain

- [x] Implement append-only JSONL or SQLite-backed audit entries.
- [x] Add previous-hash and entry-hash fields.
- [ ] Add audit verification script.
- [x] Add tests for audit tampering detection.

Exit criteria:
- Audit log detects modification, deletion, and reordering where feasible.

## Milestone 3 — Key Release / HPKE-Inspired Wrapping

- [ ] Implement provider X25519 key generation.
- [ ] Implement X25519 shared secret derivation.
- [ ] Derive wrapping key using HKDF-SHA256.
- [ ] Wrap DEK using AES-GCM with release context as AAD.
- [ ] Add provider unwrap/decrypt flow.
- [ ] Add tests for wrong provider key failure.

Exit criteria:
- Gateway can release a DEK only to the intended provider key.

## Milestone 4 — ZKP Credential Proof

- [ ] Create minimal Circom circuit for credential commitment.
- [ ] Add valid and invalid sample inputs.
- [ ] Add scripts for compile/setup/prove/verify.
- [ ] Add Python verifier wrapper around snarkjs verification.
- [ ] Add tests or demo checks for valid and invalid proof.

Exit criteria:
- Valid provider proof passes.
- Invalid credential proof fails.
- Proof does not reveal raw credential secret.

## Milestone 5 — Access Gateway API

- [ ] Add FastAPI app.
- [ ] Add `/setup/demo-data`.
- [ ] Add `/records/encrypt`.
- [ ] Add `/provider/register`.
- [ ] Add `/access/request`.
- [ ] Add `/audit`.
- [ ] Add `/audit/verify`.
- [ ] Add API schemas.
- [ ] Add API tests.

Exit criteria:
- The full demo flow can run through API endpoints.

## Milestone 6 — Demo and Submission Readiness

- [ ] Add `docs/DEMO_SCRIPT.md`.
- [ ] Add `docs/PROTOTYPE_TESTING.md`.
- [ ] Add screenshots or terminal output examples if needed.
- [ ] Add final README setup instructions.
- [ ] Run full test suite.
- [ ] Review security checklist.
- [ ] Prepare final presentation/demo sequence.

Exit criteria:
- Another student can clone, install, run tests, and run the demo from README alone.
