# Skill: Sync Docs on Code Change

Use this whenever code behavior changes.

## Mapping

| Code change | Required doc update |
|---|---|
| Setup/dependency change | `README.md` |
| Endpoint change | `docs/API.md` |
| Crypto behavior change | `SECURITY.md`, maybe `AGENTS.md` |
| Database/schema change | `DATABASE.md` |
| Demo flow change | `docs/DEMO_SCRIPT.md` |
| New milestone completion | `ROADMAP.md`, `PLAN.md` |
| Non-obvious bug/decision | `LEARNINGS.md` |

## Rules

- Do not duplicate long explanations.
- Keep commands copy-pasteable.
- Use current actual command names.
- Remove stale instructions.
- Commit docs with code.
