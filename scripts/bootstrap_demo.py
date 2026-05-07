"""Create local fake SecureMed demo data."""

from __future__ import annotations

import json

from securemed.services.access_gateway import (
    bootstrap_demo,
    generate_demo_proof,
    store_for_data_dir,
)


def main() -> None:
    store = store_for_data_dir()
    result = bootstrap_demo(store)
    try:
        result["demo_proof"] = generate_demo_proof(store)
        result["zkp_ready"] = True
    except Exception as exc:  # noqa: BLE001 - CLI reports setup readiness.
        result["demo_proof"] = {"error": str(exc)}
        result["zkp_ready"] = False
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
