---
name: dead-code-removal
description: Use when code, docs, dependencies, tests, or helpers become unused, duplicated, misleading, or inconsistent with SecureMed prototype scope.
---

# Skill: Remove Dead or Stale Code

Use this skill when code becomes unused, duplicated, misleading, or inconsistent with the paper scope.

## When to Use

- An old helper is no longer imported.
- A TODO points to a feature outside scope.
- A mock was replaced by a real implementation.
- A duplicate implementation exists.
- A file describes behavior that no longer exists.
- A dependency is no longer used.

## Procedure

- [ ] Search references before deleting.
- [ ] Check tests.
- [ ] Remove unused imports/functions/files.
- [ ] Remove stale docs or update them.
- [ ] Remove unused dependencies.
- [ ] Run tests.
- [ ] Commit with `chore:` or `refactor:`.

## Safety

Do not delete migration/data files, generated proof artifacts needed for demo, requested docs, or tests unless they are obsolete and replaced.
