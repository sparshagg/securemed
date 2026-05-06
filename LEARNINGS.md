# LEARNINGS.md — SecureMed Development Learnings

Use this file as an append-only project memory. Add short entries whenever the agent discovers something non-obvious, fixes a bug, updates a technical decision, or learns a library constraint.

Keep entries concise and useful.

## Format

```md
## YYYY-MM-DD — Short title

**Context:** What was being done.  
**Learning:** What was discovered.  
**Decision/Impact:** What changed because of it.  
**Files touched:** Relevant files.
```

## Initial Notes

## 2026-05-06 — Project scope locked to academic prototype

**Context:** Repository setup for SecureMed.  
**Learning:** The prototype should demonstrate the paper-required cryptographic workflow only.  
**Decision/Impact:** Avoid production EMR integration, real patient data, blockchain, cloud deployment, and complex frontend until the core cryptographic flow is complete.  
**Files touched:** `AGENTS.md`, `README.md`, `ROADMAP.md`, `PLAN.md`, `SECURITY.md`, `DATABASE.md`.

## 2026-05-06 — First crypto slice uses JSONL before SQLite

**Context:** Implementing the first runnable backend slice.  
**Learning:** JSONL is sufficient for testing hash-chain audit behavior before API query needs exist.  
**Decision/Impact:** Keep first storage simple, then move to SQLite only when FastAPI endpoints need queryable state.  
**Files touched:** `backend/securemed/storage/audit.py`, `backend/tests/test_crypto_slice.py`, `DATABASE.md`.

## 2026-05-06 — AESGCM includes tag in ciphertext

**Context:** Implementing AES-256-GCM with Python `cryptography`.  
**Learning:** `AESGCM.encrypt` returns ciphertext with the 16-byte tag appended, and `decrypt` rejects wrong ciphertext, key, nonce, or AAD with `InvalidTag`.  
**Decision/Impact:** Store one `ciphertext_b64` field plus `nonce_b64` for the first encrypted payload representation.  
**Files touched:** `backend/securemed/crypto/aes_gcm.py`, `SECURITY.md`.
