---
name: secure-crypto-implementation
description: Use for SecureMed cryptography, ZKP, key release, access-control, consent, revocation, provenance, and audit-security changes.
---

# Skill: Secure Crypto Implementation

Use this skill for any change under `backend/securemed/crypto`, `backend/securemed/zkp`, or access-control code.

## Principles

- Do not invent cryptographic primitives.
- Use high-level library APIs.
- Keep keys separated by purpose.
- Prefer explicit data encoding.
- Fail closed on verification errors.
- Add negative tests.

## Required Checks

### AES-GCM

- [ ] Random nonce generated for every encryption.
- [ ] Nonce/key pair is never reused.
- [ ] AAD binds record/release context.
- [ ] Decryption failure stops the flow.

### ECDSA

- [ ] Use P-256 unless docs require a different curve.
- [ ] Sign canonical bytes, not unstable Python dict ordering.
- [ ] Verify before trusting data.

### X25519 / HKDF

- [ ] Use X25519 for shared secret.
- [ ] Use HKDF-SHA256 to derive wrapping key.
- [ ] Use context-specific `info`.
- [ ] Use AAD with release context.
- [ ] Wrong provider key must fail.

### ZKP

- [ ] Proof verification is necessary but not sufficient.
- [ ] Also check consent and revocation.
- [ ] Do not log raw witness values or secrets.
- [ ] Keep circuit minimal.

## Required Tests

Add valid and negative tests for encryption, signatures, key wrapping, proof verification, revocation, and consent denial.
