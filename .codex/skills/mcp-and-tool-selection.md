# Skill: MCP and Tool Selection

Use this before adding external tools, MCP servers, services, or integrations.

## Rule

Do not add tools because they are interesting. Add them only when they directly support the paper-required prototype.

## Procedure

- [ ] Identify the problem the tool solves.
- [ ] Check official docs.
- [ ] Check maintenance status.
- [ ] Check security implications.
- [ ] Check whether a simpler local solution is enough.
- [ ] Ask the user before adding a new external service or MCP server.

## Default Decision

For SecureMed, prefer local tools: Python, FastAPI, cryptography, pytest, Circom/snarkjs, SQLite/JSON.

Avoid cloud services unless explicitly requested.
