# SECURITY.md — SecureMed Security Model

This file defines the security expectations for the SecureMed prototype.

## 1. Security Objective

SecureMed demonstrates how an electronic medical record can be shared only after cryptographic and policy checks succeed.

The prototype must prove:

1. Unauthorised users cannot decrypt the fake EMR.
2. Tampered ciphertext is rejected.
3. Tampered provenance is rejected.
4. Invalid or revoked provider credentials are denied.
5. Record access decisions are audit logged.
6. Audit log tampering is detectable.
7. Provider eligibility can be proven without revealing the raw credential secret.

## 2. Threat Model

### In Scope

- Network eavesdropper.
- Tampered ciphertext.
- Tampered metadata.
- Invalid provider credential.
- Revoked provider credential.
- Replay-style reuse of stale access request in a simplified local demo.
- Malicious user modifying audit logs.
- Repository/database compromise where attacker reads stored ciphertext.
- Mistaken developer committing secrets.

### Out of Scope

- Real hospital attackers.
- Real production medical systems.
- Hardware side-channel attacks.
- Full insider threat against HSM/KMS administrators.
- Nation-state quantum adversary.
- Full anonymous credential system.
- Full regulatory compliance validation.
- Browser/device malware after the provider decrypts the record.

## 3. Cryptographic Mechanisms

| Mechanism | Role |
|---|---|
| AES-256-GCM | Encrypt fake EMR content and authenticate ciphertext/AAD |
| ECDSA P-256 | Sign and verify record provenance |
| SHA-256 | Hash manifests, records, and audit chain inputs |
| X25519 | Establish shared secret for DEK wrapping |
| HKDF-SHA256 | Derive wrapping key from X25519 shared secret |
| AES-GCM wrapping | Wrap per-record DEK to provider |
| Circom/snarkjs ZKP | Prove provider eligibility without revealing raw credential |
| Hash-chained audit log | Detect tampering with access records |

## 4. Required Negative Tests

Every security-sensitive feature must have negative tests.

Required tests:

- [x] AES-GCM decrypt fails when ciphertext is modified.
- [x] AES-GCM decrypt fails when AAD is modified.
- [x] Signature verification fails when manifest is modified.
- [ ] Provider cannot unwrap DEK with wrong private key.
- [ ] Invalid ZKP is rejected.
- [ ] Revoked credential is rejected even if proof is otherwise valid.
- [ ] Consent-denied access request does not release DEK.
- [x] Audit chain verification fails after event modification.
- [x] Audit chain verification fails after event deletion or reordering where feasible.

## 5. Secrets and Sensitive Files

Never commit:

- `.env`
- private keys
- generated provider private keys
- hospital signing private key
- snarkjs `.ptau` files if generated locally
- proving keys if they are large or contain setup-sensitive material
- local SQLite database with generated secrets
- local audit logs with secrets
- Python caches
- node_modules
- coverage reports

Commit only fake public keys if needed, fake sample data, small example inputs, documentation, and deterministic test fixtures that contain no secrets.

## 6. AES-GCM Rules

- Generate a fresh 96-bit nonce for every encryption under a given key.
- Never reuse nonce/key pairs.
- Bind important context as AAD: record ID, record version, origin institution, and release ID where applicable.
- Do not ignore authentication failures.
- Do not log plaintext or DEKs.

Current implementation uses `cryptography` `AESGCM`, 256-bit DEKs, random
12-byte nonces, and ciphertext values with the 16-byte authentication tag
appended by the library.

## 7. Signature Rules

- The origin institution or clinician signs record provenance.
- The patient signs consent artefacts if implemented.
- The patient should not be treated as signing the clinical truth of the medical record.
- Verify signatures before trusting manifests.
- Use canonical JSON or stable byte encoding before signing.

## 8. ZKP Rules

The ZKP proves eligibility, not identity and not non-repudiation.

Correct claim:

> The provider can prove possession of a valid credential satisfying the access predicate without revealing the raw credential secret.

Incorrect claim:

> ZKP alone provides non-repudiation.

Non-repudiation must come from signatures and audit logs.

## 9. Access Gateway Rules

Before releasing a DEK, the gateway must check proof validity, credential expiry, credential revocation, patient consent or emergency override, requested purpose, record existence, and provider key binding.

If any check fails, do not release the DEK.

## 10. Audit Rules

Audit entries must include event ID, timestamp, record ID, provider ID or audit handle, credential commitment, action, reason, previous hash, and entry hash.

Never include plaintext EMR, DEK, private keys, or raw credential secret.

Current implementation stores audit events as local JSONL and verifies both the
`previous_hash` link and canonical entry hash.

## 11. Security Review Before Submission

Before final demo:

- [ ] Run all tests.
- [ ] Search repository for `PRIVATE KEY`.
- [ ] Search repository for `.env`.
- [ ] Search repository for fake/real patient leakage.
- [ ] Verify no actual medical data is present.
- [ ] Verify README warns users this is academic only.
- [ ] Verify every failed security condition creates a denied audit entry.
