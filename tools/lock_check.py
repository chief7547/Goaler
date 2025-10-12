#!/usr/bin/env python3
"""Manage the manifest lock file."""

import argparse
import json
import sys
from pathlib import Path

LOCK = Path("audit/manifest.lock")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--init", action="store_true")
    args = parser.parse_args()

    if not LOCK.exists():
        if args.init:
            LOCK.parent.mkdir(parents=True, exist_ok=True)
            LOCK.write_text(json.dumps({"lock": "created"}), encoding="utf-8")
            print("Lock created")
        else:
            print(
                "LOCK missing. Run with --init to create after review.",
                file=sys.stderr,
            )
            sys.exit(2)
    else:
        print("Lock present")


if __name__ == "__main__":
    main()
