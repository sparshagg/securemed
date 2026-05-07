# DATABASE.md — SecureMed Prototype Storage Design

This file defines the storage model. Keep it updated whenever schemas change.

The prototype can start with JSON files and later move to SQLite if needed. Prefer SQLite once API endpoints exist.

Current implementation uses JSON files and JSONL for the local demo. SQLite is
not needed for the academic prototype.

## 1. Storage Principles

- Store fake data only.
- Store encrypted records, not plaintext records.
- Store public keys and commitments, not raw credential secrets.
- Store audit events without plaintext EMRs or DEKs.
- Keep schema simple and easy to inspect for grading/demo.

## 2. Data Stores

Expected local stores:

```text
data/
  audit.jsonl
  records.json
  providers.json
  consent_policies.json
  revoked_credentials.json
  private/
    record_keys.json
    provider_private.json
  zk/
    credential_input.json
    proof.json
    public.json
    credential_witness.wtns
```

These are runtime artifacts and should generally not be committed unless they are tiny fake fixtures.

Committed fixture data currently lives in `sample_data/fake_emr_record.json` and
contains only fake FHIR-like demo data.

## 3. Tables / Collections

### records

Stores encrypted fake EMRs.

| Field | Type | Description |
|---|---|---|
| `record_id` | text primary key | Stable fake record ID |
| `patient_pseudonym` | text | Pseudonymous patient handle |
| `ciphertext_b64` | text | AES-GCM ciphertext |
| `nonce_b64` | text | AES-GCM nonce |
| `tag_b64` | text or included | Auth tag if library stores separately |
| `aad_json` | text | Associated data used for encryption |
| `manifest_json` | text | Signed record provenance manifest |
| `manifest_signature_b64` | text | ECDSA signature |
| `created_at` | text | ISO timestamp |
| `version` | integer | Record version |

### record_keys

Stores DEKs wrapped or sealed for internal use.

| Field | Type | Description |
|---|---|---|
| `record_id` | text | Linked record |
| `wrapped_dek_b64` | text | DEK wrapped under local demo KEK or sealed test key |
| `wrap_alg` | text | Example: `LOCAL-DEMO-AESGCM` |
| `key_version` | integer | KEK/key version |
| `created_at` | text | ISO timestamp |

Current JSON demo stores raw DEKs in ignored `data/private/record_keys.json`
only so the local gateway can demonstrate later release wrapping. This file must
never be committed.

### providers

Stores provider public information.

| Field | Type | Description |
|---|---|---|
| `provider_id` | text primary key | Demo provider ID |
| `provider_label` | text | Human-readable fake provider name |
| `x25519_public_key_b64` | text | Public key for DEK release |
| `signature_public_key_pem` | text | Optional provider signing public key |
| `credential_commitment` | text | Public ZKP commitment |
| `role_code` | integer | Demo role code |
| `status` | text | active/revoked |
| `created_at` | text | ISO timestamp |

### consent_policies

Stores simple consent decisions.

| Field | Type | Description |
|---|---|---|
| `consent_id` | text primary key | Consent artefact ID |
| `record_id` | text | Target record |
| `provider_id` | text | Provider allowed/denied |
| `purpose` | text | Example: `treatment`, `insurance`, `emergency` |
| `decision` | text | allow/deny |
| `expires_at` | text | ISO timestamp |
| `signature_b64` | text | Optional consent signature |
| `created_at` | text | ISO timestamp |

### revoked_credentials

Stores revoked provider credential commitments.

| Field | Type | Description |
|---|---|---|
| `credential_commitment` | text primary key | Revoked commitment |
| `reason` | text | Example: expired, suspended, compromised |
| `revoked_at` | text | ISO timestamp |

### audit_events

Stores access attempts. Can be SQLite table or JSONL.

| Field | Type | Description |
|---|---|---|
| `event_id` | text primary key | Unique event |
| `timestamp` | text | ISO timestamp |
| `record_id` | text | Target record |
| `provider_id` | text | Provider ID or pseudonymous handle |
| `credential_commitment` | text | Credential commitment, not raw secret |
| `action` | text | ACCESS_GRANTED or ACCESS_DENIED |
| `reason` | text | Decision reason |
| `release_id` | text | Release manifest ID if granted |
| `previous_hash` | text | Previous event hash |
| `entry_hash` | text | Current event hash |

## 4. Runtime Files Not to Commit

Add to `.gitignore`:

```text
data/
*.sqlite3
*.db
audit.jsonl
keys/private/
keys/generated/
circuits/build/
circuits/*.zkey
circuits/*.ptau
```

## 5. Database Change Rule

When a schema changes:

- [ ] Update this file.
- [ ] Update code models.
- [ ] Update tests.
- [ ] Update README if setup commands change.
- [ ] Add a learning if the change fixed a bug or clarified architecture.
