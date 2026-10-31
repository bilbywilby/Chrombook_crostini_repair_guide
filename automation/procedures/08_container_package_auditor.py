#!/usr/bin/env python3
import subprocess

def audit_packages():
    print("=== Container Package Auditor ===")
    try:
        result = subprocess.run(["dpkg", "--audit"], capture_output=True, text=True, timeout=10)
        if result.stdout.strip():
            print(f"[ISSUE] Broken packages detected:\n{result.stdout}")
        else:
            print("[PASS] No broken packages detected.")
    except Exception as e:
        print(f"[ERROR] dpkg audit failed: {e}")
    
    try:
        result = subprocess.run(["apt", "list", "--upgradable"], capture_output=True, text=True, timeout=15)
        updates = [line for line in result.stdout.splitlines() if line.strip()]
        if len(updates) > 1:
            print(f"[INFO] {len(updates)-1} packages have pending updates.")
        else:
            print("[PASS] System is up to date.")
    except Exception as e:
        print(f"[ERROR] Update check failed: {e}")

if __name__ == "__main__":
    audit_packages()
