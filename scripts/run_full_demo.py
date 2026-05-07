"""Run the full SecureMed local demo flow."""

from __future__ import annotations

import json

from securemed.services.access_gateway import (
    DEFAULT_PROVIDER_ID,
    DEFAULT_PURPOSE,
    DEFAULT_RECORD_ID,
    bootstrap_demo,
    decrypt_as_demo_provider,
    generate_demo_proof,
    request_access,
    store_for_data_dir,
    verify_audit,
)


def main() -> None:
    store = store_for_data_dir()
    bootstrap_demo(store)
    proof = generate_demo_proof(store)
    decision = request_access(
        store,
        record_id=DEFAULT_RECORD_ID,
        provider_id=DEFAULT_PROVIDER_ID,
        purpose=DEFAULT_PURPOSE,
        zkp_proof=proof["proof"],
        zkp_public_signals=proof["public_signals"],
    )
    decrypted = decrypt_as_demo_provider(
        store,
        provider_id=DEFAULT_PROVIDER_ID,
        access_decision=decision,
    )
    print(
        json.dumps(
            {
                "decision": decision.__dict__,
                "provider_decrypted_record": decrypted,
                "audit": verify_audit(store),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
