# FastAPI Dependency Patterns

Use this reference when adding shared FastAPI dependencies.

## Defaults

- Prefer `Annotated[T, Depends(dep)]` for dependencies.
- Create reusable dependency type aliases for dependencies used by multiple endpoints.
- Use router-level `dependencies=[Depends(...)]` for checks that apply to every route in a router.
- Use `yield` dependencies only when setup/cleanup is required.
- Keep blocking dependencies as regular `def` functions unless they call async code.

## SecureMed Notes

- Do not put plaintext EMRs, DEKs, private keys, or raw credential secrets in dependencies.
- Keep access-control decisions explicit in service code; dependencies may load state but should not hide cryptographic policy.
- Prefer simple local JSON/SQLite resource dependencies until production infrastructure is explicitly in scope.

