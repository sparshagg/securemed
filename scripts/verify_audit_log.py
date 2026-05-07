"""Verify the local SecureMed JSONL audit log."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from securemed.storage.audit import AuditLogVerificationError, verify_audit_log


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "audit_log", nargs="?", type=Path, default=Path("data/audit.jsonl")
    )
    args = parser.parse_args()
    try:
        result = verify_audit_log(args.audit_log)
        print(json.dumps(result.__dict__, indent=2, sort_keys=True))
    except AuditLogVerificationError as exc:
        raise SystemExit(f"audit log invalid: {exc}") from exc


if __name__ == "__main__":
    main()
