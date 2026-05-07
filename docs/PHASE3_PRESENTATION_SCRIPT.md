# Phase III Presentation Review and 3-Minute Script

Use this for the final Phase III presentation. The attached PPT is strong for the Phase II design story, but the Phase III presentation should explicitly say what is implemented now.

## PPT Correctness Review

Overall: the deck is mostly correct as a Phase I/II design deck and matches the Phase II report well. For Phase III, it needs small wording changes so it does not overclaim production features that the prototype intentionally simulates locally.

Recommended fixes before presenting:

- Slide 1: change "Phase I & II Combined Report" to "Phase III Prototype Demo" or "Phase III Implementation".
- Slide 4: replace "HPKE / X25519" with "X25519 + HKDF-SHA256 + AES-GCM DEK wrapping". The prototype uses the same HPKE-style KEM/DEM idea, but not a full RFC 9180 HPKE library.
- Slide 4 and Slide 9: HMAC-SHA-256 is in the Phase II design, but the current prototype focuses on AES-GCM, ECDSA, SHA-256, ZKP, X25519 wrapping, consent, revocation, and hash-chained audit. Do not present HMAC as implemented unless you add it.
- Slide 5: KMS/HSM, credential issuer, and patient consent app are architectural components from the design. In the prototype, they are simulated with local JSON state and runtime-generated keys.
- Slide 6: "DEK sealed in KMS/HSM" should be described as "stored only in ignored local runtime state for the demo." This is acceptable for an academic prototype but must not be described as a real KMS.
- Slide 9: consent signatures, release-manifest signatures, and signed audit entries are design goals from Phase II. The implementation signs provenance and hash-chains audit entries. Consent and release are checked/recorded locally, not fully signed.
- Slide 10: replace "suitable for production use" with "compact and fast enough for the prototype." Production use would require circuit audit and trusted setup governance.
- Slide 15: change "ZK/mock-ZK" to "real Circom/snarkjs ZKP" because the Phase III prototype now uses an actual Groth16 proof flow.

Best 3-minute slide path:

1. Slide 1: title.
2. Slide 2: problem.
3. Slide 4: solution primitives.
4. Slide 6: workflow.
5. Slide 10: ZKP.
6. Live demo.
7. Slide 15: conclusion.

Do not try to present all 15 slides in 3 minutes. Use the rest only as backup slides for questions.

## Pre-Demo Setup

Run these before the presentation starts:

```bash
cd /Users/sparshaggarwal/Projekts/securemed
python scripts/setup_zkp.py
fastapi run --host 127.0.0.1 --port 8000
```

Open:

```text
http://127.0.0.1:8000/demo
http://127.0.0.1:8000/docs
```

Keep the demo page visible. If the browser demo has any issue, use the backup CLI:

```bash
python scripts/run_full_demo.py
python scripts/verify_audit_log.py
```

## 3-Minute Two-Speaker Script

Target length: about 390-430 spoken words.

### 0:00-0:20 — Speaker 1, Title and Problem

Good morning. We are presenting SecureMed, our Phase III implementation for secure medical record sharing using hybrid encryption and zero-knowledge proofs.

The problem is that normal healthcare systems usually protect the channel, for example using TLS, but once a record reaches an application server or database, it may exist in plaintext. For medical data, that is a serious risk because a leaked diagnosis or prescription history cannot be reset like a password.

### 0:20-0:50 — Speaker 2, Design Goal

Our goal is to protect the medical record as an encrypted object, not only as network traffic. The prototype uses fake EMR data only. Each record is encrypted with AES-256-GCM using a fresh data encryption key. We also sign a provenance manifest using ECDSA P-256, so the receiver can verify where the encrypted record came from and detect tampering.

### 0:50-1:20 — Speaker 1, Access Control and ZKP

Access is not granted just because someone asks for the record. The provider must prove credential eligibility using a real Circom and snarkjs Groth16 zero-knowledge proof. The proof shows that the provider has a valid credential commitment, the required role, and a non-expired credential, without revealing the raw credential secret.

The gateway also checks consent and revocation separately. This is important because a valid proof alone is not enough if the patient has not consented or the credential has been revoked.

### 1:20-1:50 — Speaker 2, Key Release and Audit

If all checks pass, the gateway does not send the plaintext record. Instead, it wraps the per-record DEK to the provider using X25519 key agreement, HKDF-SHA256, and AES-GCM. The wrapping context is bound to the record ID, provider ID, credential commitment, purpose, and release ID.

Every grant or denial is written to a JSONL audit log. Each entry includes the previous hash, so editing, deleting, or reordering events breaks audit verification.

### 1:50-2:35 — Speaker 1, Live Demo

Now we will demonstrate the implemented flow.

First, we click "Setup demo data." This creates a fake encrypted EMR, registers a demo provider, creates consent, and generates a real ZKP proof.

Next, we click "Request access." The gateway verifies the ZKP, checks that the credential is not revoked, confirms consent for the purpose, and then releases a wrapped DEK. The output shows `ACCESS_GRANTED`, the encrypted record, the signed provenance manifest, and the wrapped DEK.

Finally, we click "Verify audit." The audit chain verifies successfully, showing that the access event has been recorded in a tamper-evident way.

### 2:35-3:00 — Speaker 2, Conclusion

So the Phase III prototype demonstrates the complete cryptographic workflow from our report: fake EMR creation, AES-GCM encryption, ECDSA provenance signing, real ZKP credential verification, consent and revocation checks, X25519-based DEK release, provider-side decryption support, and hash-chained audit logging.

The prototype is intentionally local and academic. It does not use real patient data, real hospital systems, or a production KMS. But it proves the core security idea: the record stays encrypted until the requester proves eligibility and passes policy checks, and every decision is auditable.

## Backup Demo Lines

If the browser demo fails, say:

"The browser is only a small interface over the same backend. We will use the CLI fallback, which runs the same cryptographic flow."

Then run:

```bash
python scripts/run_full_demo.py
```

Point out these outputs:

- `decision: ACCESS_GRANTED`
- `provider_decrypted_record`
- `provenance_verified: true`
- `audit_valid: true`

Then run:

```bash
python scripts/verify_audit_log.py
```

Say:

"This confirms the audit chain is intact. The tests also cover denial cases, including invalid proofs, revoked credentials, consent denial, and tampered ciphertext or AAD."

## Likely Questions and Short Answers

Question: Is this production ready?

Answer: No. It is an academic prototype. Production would need real identity integration, HSM/KMS, audited ZKP circuits, operational consent workflows, and compliance review.

Question: Is the ZKP mocked?

Answer: No. The current prototype uses a real Circom circuit and snarkjs Groth16 proof verification.

Question: Why not just use TLS?

Answer: TLS protects data in transit, but SecureMed protects the EMR object itself after storage and before release.

Question: What does the audit log prove?

Answer: It makes access history tamper-evident. If an old grant or denial is edited, deleted, or reordered, verification fails.

Question: Where is real patient data stored?

Answer: Nowhere. The repo uses fake sample EMR data only.
