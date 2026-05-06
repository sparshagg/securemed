# AGENTS.md — SecureMed Prototype Source of Truth

This file is the project-level source of truth for AI agents working on the SecureMed prototype. Follow it before any other repository-local instruction. Keep it accurate, concise, and updated whenever code or architecture changes.

## 1. Project Identity

**Project name:** SecureMed Prototype  
**Course context:** Cryptography — Innovation & Implementation Exercise, Phase III prototype preparation  
**Project theme:** Secure Medical Record Sharing Using Hybrid Encryption and Zero-Knowledge Proofs  
**Primary goal:** Build a minimal, high-quality, locally runnable prototype that demonstrates the cryptographic workflow described in the Phase I/II report.

SecureMed is **not** a production healthcare system. It is an academic cryptography prototype demonstrating core security properties using fake medical records only.

## 2. Strict Scope: Do What the Paper Demands

Implement only what is necessary to demonstrate the cryptographic system:

1. Fake EMR/FHIR-like JSON record creation.
2. AES-256-GCM record encryption and decryption.
3. ECDSA P-256 provenance signing and verification.
4. X25519 + HKDF-SHA256 + AES-GCM key-wrapping flow for release of the per-record DEK.
5. RSA-OAEP compatibility path only if time remains; it must not replace the X25519/HPKE-style main path.
6. Zero-knowledge proof of provider credential eligibility using Circom/snarkjs.
7. Consent and revocation checks using simple local state.
8. Hash-chained audit logs.
9. FastAPI backend endpoints for demo/testing.
10. Clear README instructions and tests.

Do **not** build real hospital integration, real patient records, production auth, blockchain, payment systems, cloud deployment, full OpenMRS integration, complex frontend unless the backend prototype is complete, or post-quantum cryptography beyond a documented future-scope note.

## 3. Required Security Properties and Mechanism Mapping

| Security property | Prototype mechanism |
|---|---|
| Confidentiality | AES-256-GCM encrypts EMR content; DEK released only after proof, policy, consent, and revocation checks |
| Integrity | AES-GCM tag, ECDSA signatures, SHA-256 hashes, hash-chained audit log |
| Authentication | ECDSA provenance signature; provider credential proof verification |
| Non-repudiation | Signed provenance and signed/hashed audit entries |
| Privacy-preserving eligibility | ZKP proves provider eligibility without revealing the raw credential secret |
| Access control | Gateway verifies ZKP, consent, revocation, and purpose before DEK release |
| Auditability | Append-only JSONL audit log with previous-hash chaining |

## 4. Preferred Tech Stack

- **Language:** Python 3.11+
- **Backend:** FastAPI
- **Crypto library:** `cryptography`
- **ZKP tooling:** Circom + snarkjs
- **Storage:** SQLite or JSON files; prefer SQLite if queries are needed
- **Testing:** pytest
- **Formatting/linting:** ruff
- **Docs:** Markdown

The prototype should be runnable locally on macOS/Linux. Windows support is optional.

## 5. Repository Shape

Target structure:

```text
securemed-prototype/
  AGENTS.md
  README.md
  ROADMAP.md
  PLAN.md
  SECURITY.md
  DATABASE.md
  LEARNINGS.md
  pyproject.toml
  backend/
    securemed/
      main.py
      crypto/
      zkp/
      storage/
      api/
    tests/
  circuits/
  scripts/
  sample_data/
  docs/
  .codex/
    skills/
    workflows/
```

If a simpler structure is chosen, update this file and README.md with the reason.

## 6. Senior Developer Operating Rules

Act like a senior software developer with applied cryptography expertise.

Before writing code:
- enter plan mode,
- inspect repository state,
- read AGENTS.md, PLAN.md, ROADMAP.md, SECURITY.md, DATABASE.md, and relevant files,
- search current official documentation for libraries/tools being changed,
- check whether an existing skill/workflow already covers the task,
- ask the user if requirements are ambiguous.

When writing code:
- write minimal code that directly supports the prototype,
- prefer simple, explicit functions over clever abstractions,
- keep cryptographic boundaries clear,
- never invent cryptography,
- never store secrets in Git,
- never use real patient data,
- avoid stale/deprecated APIs,
- add tests for every security-sensitive change,
- update docs in the same change.

When unsure:
- do not hallucinate,
- do not silently choose a risky design,
- ask a clear question with the smallest set of options.

## 7. Documentation Update Rule

Every substantial code change must update the relevant documentation:

| Change type | Docs to update |
|---|---|
| New setup command | README.md |
| New API endpoint | README.md and docs/API.md |
| Crypto design change | AGENTS.md and SECURITY.md |
| Database/schema change | DATABASE.md |
| New milestone/status | PLAN.md and ROADMAP.md |
| New lesson/bug/decision | LEARNINGS.md |
| New demo step | docs/DEMO_SCRIPT.md or docs/PROTOTYPE_TESTING.md |

Do not repeat the full architecture in every file. Link or refer to the canonical file instead.

## 8. Plan Mode and Task Tracking

Always maintain PLAN.md.

Use checkbox format:

```md
- [ ] Pending task
- [x] Completed task
- [~] In progress task
- [!] Blocked task
```

Before starting a task:
1. Add or update a checkbox in PLAN.md.
2. Mark it `[~]`.
3. Write a brief implementation plan.
4. Implement.
5. Run tests.
6. Mark it `[x]`.
7. Record lessons in LEARNINGS.md if anything non-obvious was discovered.

## 9. Branch, Commit, and Push Rules

Use a new branch for each meaningful unit of work.

Branch naming:

```text
feat/<short-feature-name>
fix/<short-bug-name>
docs/<short-doc-name>
chore/<short-maintenance-name>
security/<short-security-change>
```

Commit style:

```text
feat: add AES-GCM record encryption
fix: reject tampered audit chain entries
docs: update prototype setup guide
security: enforce nonce uniqueness checks
test: add invalid credential proof test
```

After every substantial change:
1. run tests,
2. run lint/format if configured,
3. update docs,
4. commit changes,
5. push the branch.

If push/auth fails, do not retry blindly. Ask the user.

Never commit `.env`, private keys, generated toxic waste from ZKP trusted setup, real medical data, large build artifacts, local caches, secrets, or credentials.

## 10. Security Rules

This project is about cryptography, so security quality is not optional.

Mandatory:
- Use random 96-bit nonce for each AES-GCM encryption unless official docs specify otherwise.
- Never reuse AES-GCM nonce with the same key.
- Use `cryptography` high-level primitives where possible.
- Use HKDF-SHA256 after X25519 shared secret derivation.
- Verify signatures before trusting signed metadata.
- Bind key-wrapping AAD/context to record ID, requester ID/commitment, and release ID.
- Treat ZKP verification as necessary but not sufficient; also check consent and revocation.
- Store only fake data.
- Add negative tests for tampering and invalid proof cases.

Forbidden:
- homemade crypto,
- ECB mode,
- CBC without authentication,
- plain SHA-256 as an authentication mechanism,
- global static encryption keys,
- hardcoded private keys,
- logging plaintext EMRs or secrets,
- disabling certificate/security checks to “make it work.”

## 11. ZKP Prototype Rules

The ZKP circuit must remain minimal.

Preferred statement:

> The provider knows a private credential secret and role code such that the public credential commitment is valid, the role satisfies the required role, and the credential expiry date is after today's date.

Acceptable simplification:
- Use Poseidon hash commitment in the circuit.
- Keep revocation check outside the circuit using a local revoked commitment list.
- Use Groth16 for the academic prototype.

Do not attempt a full anonymous credential system unless explicitly requested.

## 12. Quality Gates

A change is not complete unless tests pass, docs match code, no secrets are committed, security-sensitive behavior has a negative test, PLAN.md is updated, and LEARNINGS.md is updated when needed.

## 13. Ask-the-User Triggers

Ask the user before changing cryptographic architecture, adding a framework, replacing the ZKP approach, adding cloud services, integrating real EMR systems, adding a frontend that changes scope, changing branch/commit automation behavior, or pushing to a protected branch.
