#!/usr/bin/env python3
"""
tools/golden_check.py
- manifest의 golden_checks를 읽어 sha256 체크를 수행합니다.
- 실패 시 non-zero exit를 반환해 CI를 실패시킵니다.
"""
import hashlib, yaml, sys, pathlib, re
def load_manifest(path="VIBECODE_ENTRY.md"):
    txt=open(path,"r",encoding="utf-8").read()
    s=txt.find("```yaml")
    e=txt.find("```",s+6)
    return yaml.safe_load(txt[s+6:e])

def sha(path):
    b=pathlib.Path(path).read_bytes()
    return hashlib.sha256(b).hexdigest()

def main():
    manifest=load_manifest()
    golden = manifest.get("golden_checks",{})
    bad=[]
    for p,h in golden.items():
        if not pathlib.Path(p).exists():
            bad.append(f"missing:{p}")
            continue
        if sha(p)!=h:
            bad.append(f"mismatch:{p}")
    if bad:
        print("Golden check failed:", bad)
        sys.exit(2)
    print("Golden verified")
if __name__=="__main__":
    main()
