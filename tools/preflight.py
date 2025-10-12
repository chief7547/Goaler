#!/usr/bin/env python3
"""Preflight checks for the Vibecoding manifest."""

from __future__ import annotations

import argparse
import os
import pathlib
import sys

import yaml
from dotenv import load_dotenv


def load_manifest(path: str) -> dict:
    """Extract the YAML manifest block from the entry file."""

    text = pathlib.Path(path).read_text(encoding="utf-8")
    try:
        manifest_section = text.split("## 매니페스트")[1].split("---")[0]
    except IndexError as exc:
        raise SystemExit("manifest section not found") from exc

    start = manifest_section.find("```yaml\n")
    if start == -1:
        raise SystemExit("manifest code fence not found")

    end = manifest_section.find("```", start + 7)
    if end == -1:
        raise SystemExit("manifest code fence terminator not found")

    yaml_text = manifest_section[start + 7 : end].strip()
    return yaml.safe_load(yaml_text)


def check_secrets(manifest: dict) -> list[str]:
    """Return missing environment variables defined in the manifest."""

    required = (
        manifest.get("preflight", {})
        .get("checks", {})
        .get("secrets_bound", {})
        .get("required_keys", [])
    )
    return [key for key in required if os.environ.get(key) is None]


def check_required_files(manifest: dict) -> list[str]:
    """Return missing files that the manifest expects to exist."""

    missing: list[str] = []
    for path_str in manifest.get("required_files", []):
        if not pathlib.Path(path_str).exists():
            missing.append(path_str)
    return missing


def main() -> None:
    load_dotenv()

    parser = argparse.ArgumentParser()
    parser.add_argument("--entry", required=True)
    parser.add_argument("--init-lock-if-missing", action="store_true")
    parser.add_argument("--check-secrets", action="store_true")
    args = parser.parse_args()

    manifest = load_manifest(args.entry)

    if args.check_secrets:
        missing = check_secrets(manifest)
        if missing:
            print("Missing required env keys:", missing)
            sys.exit(3)

    missing_files = check_required_files(manifest)
    if missing_files:
        print("Missing files expected to be generated:", missing_files)

    # Lock behavior delegated to tools/lock_check.py
    print("Preflight OK")


if __name__ == "__main__":
    main()
