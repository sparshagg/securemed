"""FastAPI routes for the SecureMed local demo."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse

from securemed.api.schemas import (
    AccessRequest,
    AccessResponse,
    AuditListResponse,
    AuditVerifyResponse,
    EncryptRecordRequest,
    EncryptRecordResponse,
    ProviderRegistrationRequest,
    ProviderRegistrationResponse,
    SetupDemoResponse,
)
from securemed.services.access_gateway import (
    DEFAULT_PROVIDER_ID,
    DEFAULT_PURPOSE,
    DEFAULT_RECORD_ID,
    bootstrap_demo,
    create_signed_encrypted_record,
    generate_demo_proof,
    list_audit,
    request_access,
    store_for_data_dir,
    verify_audit,
)
from securemed.storage.json_state import DemoStore


def get_store() -> DemoStore:
    return store_for_data_dir()


StoreDep = Annotated[DemoStore, Depends(get_store)]

setup_router = APIRouter(prefix="/setup", tags=["setup"])
records_router = APIRouter(prefix="/records", tags=["records"])
providers_router = APIRouter(prefix="/provider", tags=["providers"])
access_router = APIRouter(prefix="/access", tags=["access"])
audit_router = APIRouter(prefix="/audit", tags=["audit"])
demo_router = APIRouter(tags=["demo"])


@setup_router.post("/demo-data")
def setup_demo_data(store: StoreDep) -> SetupDemoResponse:
    result = bootstrap_demo(store)
    demo_proof: dict[str, object] | None = None
    zkp_ready = False
    try:
        demo_proof = generate_demo_proof(store)
        zkp_ready = True
    except Exception as exc:  # noqa: BLE001 - API reports toolchain readiness.
        demo_proof = {"error": str(exc)}
    return SetupDemoResponse(
        record_id=DEFAULT_RECORD_ID,
        provider_id=DEFAULT_PROVIDER_ID,
        purpose=DEFAULT_PURPOSE,
        provider=result["provider"],
        consent=result["consent"],
        zkp_input_hint=result["zkp_input_hint"],
        demo_proof=demo_proof,
        zkp_ready=zkp_ready,
    )


@records_router.post("/encrypt")
def encrypt_record(
    request: EncryptRecordRequest, store: StoreDep
) -> EncryptRecordResponse:
    return EncryptRecordResponse(
        record=create_signed_encrypted_record(store, record_id=request.record_id)
    )


@providers_router.post("/register")
def register_provider(
    request: ProviderRegistrationRequest,
    store: StoreDep,
) -> ProviderRegistrationResponse:
    provider = request.model_dump()
    provider["created_at"] = provider.get("created_at", "")
    store.save_provider(request.provider_id, provider)
    return ProviderRegistrationResponse(provider=provider)


@access_router.post("/request")
def request_record_access(request: AccessRequest, store: StoreDep) -> AccessResponse:
    decision = request_access(
        store,
        record_id=request.record_id,
        provider_id=request.provider_id,
        purpose=request.purpose,
        zkp_proof=request.zkp_proof,
        zkp_public_signals=request.zkp_public_signals,
    )
    return AccessResponse(**decision.__dict__)


@audit_router.get("")
def get_audit_entries(store: StoreDep) -> AuditListResponse:
    return AuditListResponse(entries=list_audit(store))


@audit_router.post("/verify")
def verify_audit_chain(store: StoreDep) -> AuditVerifyResponse:
    return AuditVerifyResponse(**verify_audit(store))


@demo_router.get("/demo", response_class=HTMLResponse)
def demo_page() -> str:
    return """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>SecureMed Demo</title>
  <style>
    body { font-family: system-ui, sans-serif; margin: 2rem; max-width: 980px; }
    button { margin: .25rem .5rem .25rem 0; padding: .55rem .8rem; }
    pre { background: #111827; color: #f9fafb; padding: 1rem; overflow: auto; }
  </style>
</head>
<body>
  <h1>SecureMed Local Demo</h1>
  <button onclick="setup()">Setup demo data</button>
  <button onclick="accessRecord()">Request access</button>
  <button onclick="verifyAudit()">Verify audit</button>
  <pre id="output">Run setup first.</pre>
  <script>
    let setupPayload = null;
    const output = document.getElementById("output");
    function show(value) { output.textContent = JSON.stringify(value, null, 2); }
    async function setup() {
      const res = await fetch("/setup/demo-data", { method: "POST" });
      setupPayload = await res.json();
      show(setupPayload);
    }
    async function accessRecord() {
      if (!setupPayload || !setupPayload.zkp_ready) {
        show({ error: "Run setup with ready ZKP artifacts first." });
        return;
      }
      const res = await fetch("/access/request", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({
          record_id: setupPayload.record_id,
          provider_id: setupPayload.provider_id,
          purpose: setupPayload.purpose,
          zkp_proof: setupPayload.demo_proof.proof,
          zkp_public_signals: setupPayload.demo_proof.public_signals
        })
      });
      show(await res.json());
    }
    async function verifyAudit() {
      const res = await fetch("/audit/verify", { method: "POST" });
      show(await res.json());
    }
  </script>
</body>
</html>
"""
