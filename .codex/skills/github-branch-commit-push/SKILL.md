---
name: github-branch-commit-push
description: Use after substantial repository changes to manage Git branches, commits, quality gates, and GitHub pushes for SecureMed.
---

# Skill: GitHub Branch, Commit, and Push

Use this skill after every substantial change.

## Branch Naming

Use:

```text
feat/<short-feature-name>
fix/<short-bug-name>
docs/<short-doc-name>
security/<short-security-change>
test/<short-test-change>
chore/<short-maintenance-name>
```

## Commit Messages

Use conventional commits:

```text
feat: add AES-GCM record encryption
fix: reject tampered audit entries
docs: update local setup instructions
security: bind DEK wrapping to release context
test: add invalid proof denial test
chore: remove stale helper
```

## Procedure

- [ ] Check `git status`.
- [ ] Create/switch branch.
- [ ] Implement.
- [ ] Run tests.
- [ ] Update docs.
- [ ] Check diff.
- [ ] Ensure no secrets.
- [ ] Commit.
- [ ] Push branch.

Push automatically only when a remote exists, auth works, branch is not protected, tests pass, and no secrets are present. If push fails, stop and ask the user.
