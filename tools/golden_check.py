#!/usr/bin/env python3
"""Verify golden files against the manifest."""

from __future__ import annotations

import hashlib
import pathlib
import sys

import yaml


def load_manifest(path: str = "VIBECODE_ENTRY.md") -> dict:
    """Load the YAML manifest block from the entry file."""

    text = pathlib.Path(path).read_text(encoding="utf-8")
    start = text.find("```yaml")
    if start == -1:
        raise SystemExit("manifest block not found")
    end = text.find("```", start + 6)
    if end == -1:
        raise SystemExit("manifest block terminator not found")
    return yaml.safe_load(text[start + 6 : end])


def digest(path: pathlib.Path) -> str:
    """Return the sha256 digest for the given file path."""

    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    manifest = load_manifest()
    golden = manifest.get("golden_checks", {})
    failures: list[str] = []

    for rel_path, expected_hash in golden.items():
        path = pathlib.Path(rel_path)
        if not path.exists():
            failures.append(f"missing:{rel_path}")
            continue
        if digest(path) != expected_hash:
            failures.append(f"mismatch:{rel_path}")

    if failures:
        print("Golden check failed:", failures)
        sys.exit(2)

    print("Golden verified")


if __name__ == "__main__":
    main()
