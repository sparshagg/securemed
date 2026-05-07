---
name: test-and-quality-gate
description: Use before marking SecureMed work complete to run tests, lint/format checks, negative security tests, docs checks, and secret-safety review.
---

# Skill: Test and Quality Gate

Use before marking any task complete.

## Required Checks

- [ ] Tests pass.
- [ ] Security negative tests exist for security-sensitive code.
- [ ] Lint/format pass if configured.
- [ ] README commands still work.
- [ ] No secrets are present.
- [ ] PLAN.md is updated.
- [ ] Relevant docs are updated.

## Expected Commands

Use configured commands. Likely:

```bash
pytest
ruff check .
ruff format .
```

Do not invent passing results. If a command cannot run, state why and ask or document the limitation.
