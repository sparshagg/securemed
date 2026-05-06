# Workflow: Documentation Sync

Use after any substantial code change.

## Steps

- [ ] Identify what changed.
- [ ] Update only the relevant documentation file.
- [ ] Avoid repeating the same explanation across files.
- [ ] Make README commands match actual commands.
- [ ] Update API docs if endpoints changed.
- [ ] Update DATABASE.md if schema/storage changed.
- [ ] Update SECURITY.md if threat model or crypto behavior changed.
- [ ] Update PLAN.md task status.
- [ ] Update LEARNINGS.md if a non-obvious issue was discovered.
- [ ] Commit docs with the code change unless the change is docs-only.

## Canonical Locations

- Source-of-truth agent behavior: `AGENTS.md`
- User run instructions: `README.md`
- Active work tracking: `PLAN.md`
- Milestones: `ROADMAP.md`
- Security details: `SECURITY.md`
- Storage/schema: `DATABASE.md`
- Lessons: `LEARNINGS.md`
