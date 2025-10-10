#!/usr/bin/env python3
"""
tools/preflight.py
- entry: path to VIBECODE_ENTRY.md
- --init-lock-if-missing : create lock only if explicitly asked
- --check-secrets : validate required env keys from manifest
"""
import os, sys, json, argparse, hashlib, pathlib, yaml, subprocess

def load_manifest(path):
    text = open(path,"r",encoding="utf-8").read()
    # manifest YAML 블록은 "## 매니페스트"와 "---" 사이에 있습니다.
    try:
        manifest_section = text.split("## 매니페스트")[1].split("---")[0]
        start = manifest_section.find("```yaml\n")
        if start==-1: raise SystemExit("manifest block not found")
        end = manifest_section.find("```", start+7)
        yaml_text = manifest_section[start+7:end].strip()
        return yaml.safe_load(yaml_text)
    except Exception as e:
        print(f"Error parsing manifest: {e}")
        sys.exit(1)

def check_secrets(manifest):
    req = manifest.get("preflight",{}).get("checks",{}).get("secrets_bound",{}).get("required_keys",[])
    missing=[]
    for k in req:
        if os.environ.get(k) is None:
            missing.append(k)
    return missing

def check_required_files(manifest):
    missing=[]
    for p in manifest.get("required_files",[]):
        if not pathlib.Path(p).exists():
            missing.append(p)
    return missing

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--entry",required=True)
    parser.add_argument("--init-lock-if-missing",action="store_true")
    parser.add_argument("--check-secrets",action="store_true")
    args=parser.parse_args()
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
if __name__=="__main__":
    main()
