# FastAPI Adjacent Tooling

Use this reference when choosing package, lint, type, database, or HTTP tooling around FastAPI.

## Defaults

- Use the project's existing package manager/configuration before adding a new one.
- Keep `ruff` for linting and formatting.
- Prefer typed Pydantic models for request and response boundaries.
- Prefer SQLModel over raw SQLAlchemy only if the project moves to a relational API model and the additional dependency is justified.
- Prefer HTTPX over Requests when adding HTTP clients.
- Do not add async/concurrency helpers unless the code actually mixes async and blocking work.

## SecureMed Notes

- Do not add cloud services, production auth, or external EMR integrations for the prototype.
- Keep runtime state local and inspectable for grading/demo.
- Check current official docs before adding or changing FastAPI-related dependencies.

