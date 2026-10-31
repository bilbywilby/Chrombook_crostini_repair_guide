#!/usr/bin/env python3
import subprocess

KEYWORDS = ["crosvm", "lxd", "termina", "vmc", "failed", "error", "timeout", "panic"]

def scan_logs():
    print("=== Crostini Log Analyzer ===")
    try:
        logs = subprocess.check_output(["dmesg"], stderr=subprocess.STDOUT).decode('utf-8', 'ignore')
        found_issues = False
        for line in logs.splitlines():
            if any(key.lower() in line.lower() for key in KEYWORDS):
                print(f"[MATCH] {line}")
                found_issues = True
        if not found_issues:
            print("[PASS] No critical Crostini-related errors found in dmesg.")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Failed to access logs: {e}")

if __name__ == "__main__":
    scan_logs()
