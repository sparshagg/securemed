---
name: create-or-update-skills
description: Use when adding or revising repository-local Codex skills. Ensures skills use the standard .codex/skills/<skill-name>/SKILL.md layout with required metadata and focused instructions.
---

# Skill: Create or Update Skills

Use this when a repeated pattern appears and no existing skill covers it.

## When to Create a Skill

Create a skill only if the same procedure will be repeated, the procedure has security or quality risk, the procedure helps avoid stale code, or the procedure improves consistency.

## Before Creating

- [ ] Check existing `.codex/skills`.
- [ ] Update an existing skill instead of duplicating.
- [ ] Use `.codex/skills/<skill-name>/SKILL.md`.
- [ ] Include YAML frontmatter with `name` and `description`.
- [ ] Keep the skill focused.
- [ ] Avoid copying AGENTS.md.

## Skill Template

```md
---
name: <skill-name>
description: Use when <trigger condition and task type>.
---

# Skill: <Name>

Use this skill when <condition>.

## Procedure

- [ ] Step 1
- [ ] Step 2
- [ ] Step 3

## Stop Conditions

Ask the user if:
- condition
- condition
```
