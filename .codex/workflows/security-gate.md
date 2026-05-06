# Workflow: Security Gate

Run this before merging or final demo.

## Checklist

- [ ] No real patient data.
- [ ] No committed private keys.
- [ ] No `.env` files.
- [ ] No generated trusted setup toxic waste.
- [ ] AES-GCM nonce uniqueness is respected.
- [ ] All cryptographic failures raise clear errors.
- [ ] ZKP verification failure denies access.
- [ ] Revoked credential denies access.
- [ ] Consent-denied request denies access.
- [ ] Audit chain tampering is detected.
- [ ] README warns that the project is academic only.
- [ ] SECURITY.md reflects actual implementation.
- [ ] Tests pass.

## Commands

Use configured commands. Expected:

```bash
pytest
ruff check .
git status --short
```

Also manually search for secrets:

```bash
grep -R "PRIVATE KEY" -n . --exclude-dir=.git || true
grep -R "BEGIN .*PRIVATE" -n . --exclude-dir=.git || true
```

Do not blindly commit if a scan returns suspicious results.
