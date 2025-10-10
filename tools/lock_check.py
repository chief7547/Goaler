#!/usr/bin/env python3
"""
tools/lock_check.py
- 락 파일 생성은 --init 옵션이 있어야만 허용됩니다.
"""
import sys, os, json, argparse, hashlib, pathlib
LOCK="audit/manifest.lock"

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--init",action="store_true")
    args=parser.parse_args()
    if not os.path.exists(LOCK):
        if args.init:
            os.makedirs(os.path.dirname(LOCK), exist_ok=True)
            json.dump({"lock":"created"}, open(LOCK,"w"))
            print("Lock created")
        else:
            print("LOCK missing. Run with --init to create after review.", file=sys.stderr)
            sys.exit(2)
    else:
        print("Lock present")
if __name__=="__main__":
    main()
