# API.md — SecureMed Prototype API

This file documents the implemented FastAPI endpoints.

## Planned Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/setup/demo-data` | Generate fake keys, fake provider, fake consent, and fake EMR |
| POST | `/records/encrypt` | Encrypt and sign a fake EMR |
| POST | `/provider/register` | Register provider public key and credential commitment |
| POST | `/access/request` | Request access to an encrypted record |
| GET | `/audit` | List audit events |
| POST | `/audit/verify` | Verify audit hash chain |
| GET | `/demo` | Tiny local demo page |

## Access Request Contract

Expected request fields:

```json
{
  "record_id": "rec_001",
  "provider_id": "provider_001",
  "purpose": "treatment",
  "zkp_proof": {},
  "zkp_public_signals": ["1", "...commitment", "7", "20580"]
}
```

Expected success response:

```json
{
  "decision": "ACCESS_GRANTED",
  "record_id": "rec_001",
  "release_id": "rel_001",
  "encrypted_record": {},
  "wrapped_dek": {},
  "provenance_manifest": {},
  "audit_event_id": "evt_001"
}
```

Expected denial response:

```json
{
  "decision": "ACCESS_DENIED",
  "record_id": "rec_001",
  "reason": "credential_revoked",
  "audit_event_id": "evt_002"
}
```

Update this file as endpoints are implemented.

## Run

```bash
python scripts/setup_zkp.py
fastapi dev
```

Open `http://127.0.0.1:8000/docs` for the interactive API docs.
