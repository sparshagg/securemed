# DEMO_SCRIPT.md — SecureMed Presentation Flow

Use this script for the final prototype demo.

## Demo Goal

Show that SecureMed can enforce secure medical record sharing using encryption, signatures, ZKP-based eligibility, key release, and tamper-evident audit logs.

## Demo 1 — Successful Access

Expected story:

```text
A valid doctor proves eligibility using a ZKP.
The gateway checks consent and revocation.
The gateway releases the encrypted record key.
The doctor decrypts the fake EMR.
The audit log records ACCESS_GRANTED.
```

Commands/endpoints will be filled after implementation.

Current full demo commands:

```bash
python scripts/setup_zkp.py
python scripts/run_full_demo.py
python scripts/verify_audit_log.py
```

For the browser demo:

```bash
fastapi dev
```

Open `http://127.0.0.1:8000/demo`.

## Demo 2 — Invalid Credential Fails

Expected story:

```text
A doctor submits an invalid proof.
The gateway rejects the request.
No DEK is released.
The audit log records ACCESS_DENIED.
```

Covered by pytest through invalid ZKP public-signal denial.

## Demo 3 — Revoked Credential Fails

Expected story:

```text
The ZKP may be mathematically valid, but the credential commitment is in the revoked list.
The gateway denies access.
```

Covered by pytest through revoked commitment denial after a valid proof.

## Demo 4 — Tampered Record Fails

Expected story:

```text
A ciphertext or manifest field is modified.
AES-GCM or ECDSA verification fails.
The plaintext is not accepted.
```

## Demo 5 — Audit Tampering Detected

Expected story:

```text
An old audit entry is edited.
Audit chain verification fails.
```

Command:

```bash
python scripts/verify_audit_log.py
```

## Final Explanation

| Demo result | Security property |
|---|---|
| Encrypted record unreadable without DEK | Confidentiality |
| Tampered record rejected | Integrity |
| Signed provenance verified | Authentication |
| Access event hash-chained | Auditability |
| Valid provider proof without raw secret | Privacy-preserving eligibility |
| Denied invalid/revoked access | Access control |
