# Workflow: Plan → Implement → Test → Commit → Push

Use this workflow for every substantial repository change.

## Steps

- [ ] Read `AGENTS.md`.
- [ ] Read task-specific docs.
- [ ] Check current git branch and status.
- [ ] Create or switch to a properly named branch.
- [ ] Update `PLAN.md` with checkbox subtasks.
- [ ] Search official documentation for libraries/tools being used.
- [ ] Implement the smallest useful change.
- [ ] Add or update tests.
- [ ] Run tests.
- [ ] Run lint/format if configured.
- [ ] Update relevant docs.
- [ ] Update `LEARNINGS.md` if a non-obvious issue was discovered.
- [ ] Review `git diff`.
- [ ] Commit using conventional commit style.
- [ ] Push if remote/auth are configured.

## Stop Conditions

Stop and ask the user if requirements conflict, cryptographic design would change, tests cannot be run, a command may destroy data, push/auth fails, or secrets appear in the diff.
