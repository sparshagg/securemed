# Skill: Latest Docs First

Use this skill before writing code that depends on external tools, libraries, frameworks, or CLIs.

## Rule

Search current official documentation before implementing or modifying code that uses FastAPI, Python `cryptography`, Circom, snarkjs, pytest, ruff, SQLite/SQLAlchemy, GitHub Actions, Docker, any MCP server, or any external integration.

## Procedure

- [ ] Identify the library/tool and version if available.
- [ ] Prefer official docs over blogs.
- [ ] Check examples for current API usage.
- [ ] Note important version constraints in `LEARNINGS.md` if relevant.
- [ ] Avoid deprecated APIs.
- [ ] If docs cannot be accessed, state the limitation and ask the user or proceed conservatively only for stable APIs.

Never base cryptographic implementation on random blog posts.
