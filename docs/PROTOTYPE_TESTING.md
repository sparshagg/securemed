# PROTOTYPE_TESTING.md — Testing Guide

This file explains how to test the SecureMed prototype.

## Test Categories

### Unit Tests

- AES-GCM encrypt/decrypt.
- ECDSA sign/verify.
- SHA-256 manifest hashing.
- X25519/HKDF key wrapping.
- Audit hash calculation.

### Negative Security Tests

- Tampered ciphertext.
- Tampered AAD.
- Tampered manifest.
- Wrong provider private key.
- Invalid ZKP.
- Revoked credential.
- Consent denied.
- Tampered audit entry.

### Integration Tests

- Full access grant flow.
- Full access deny flow.
- End-to-end record decrypt as valid provider.
- End-to-end failure as invalid provider.

## Expected Command

```bash
pytest
ruff check .
ruff format --check .
```

Current first-slice result:

```text
12 passed
```

## Test Quality Rule

A security feature is incomplete unless it has at least one success test and one failure test.

## Current Coverage

- AES-GCM encrypt/decrypt roundtrip.
- Fresh AES-GCM nonce for repeated encryption with the same DEK.
- Tampered ciphertext failure.
- Tampered AAD failure.
- ECDSA P-256 provenance signature verification.
- Tampered manifest failure.
- Wrong ECDSA public key failure.
- Valid hash-chained audit log verification.
- Modified, deleted, and reordered audit log failure.
- Audit append rejects an existing tampered chain.
