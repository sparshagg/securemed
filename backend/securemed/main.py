"""FastAPI app for the SecureMed academic prototype."""

from __future__ import annotations

from fastapi import FastAPI

from securemed.api.routes import (
    access_router,
    audit_router,
    demo_router,
    providers_router,
    records_router,
    setup_router,
)

app = FastAPI(
    title="SecureMed Prototype",
    version="0.1.0",
    description="Academic cryptography prototype using fake medical records only.",
)

app.include_router(setup_router)
app.include_router(records_router)
app.include_router(providers_router)
app.include_router(access_router)
app.include_router(audit_router)
app.include_router(demo_router)
