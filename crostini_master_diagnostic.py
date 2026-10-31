#!/usr/bin/env python3
import subprocess
import os
import sys
from pathlib import Path

PROCEDURES = [
    "automation/procedures/01_crosh_hypervisor_health_check.py",
    "automation/procedures/02_lxd_container_health_check.py",
    "automation/procedures/03_restart_unresponsive_container.py",
    "automation/procedures/04_container_safety_snapshot.py",
    "automation/procedures/05_list_container_snapshots.py",
    "automation/procedures/06_crostini_log_analyzer.py",
    "automation/procedures/07_backup_integrity_verifier.py",
    "automation/procedures/08_container_package_auditor.py",
    "automation/procedures/09_vm_resource_profiler.py",
]

def run_diagnostics():
    print("================================================")
    print("   CROSTINI FULL-STACK DIAGNOSTIC SUITE        ")
    print("================================================\n")
    
    results = {}
    for script in PROCEDURES:
        script_path = Path(script)
        if not script_path.exists():
            print(f"[SKIP] {script} (not found)")
            results[script] = "SKIP"
            continue
        
        print(f"\n>> Running: {script_path.name}")
        try:
            res = subprocess.run(["python3", str(script_path)], capture_output=True, text=True, timeout=30)
            print(res.stdout)
            results[script] = "PASS" if res.returncode == 0 else "FAIL"
        except Exception as e:
            print(f"[ERROR] {e}")
            results[script] = "ERROR"

    print("\n================================================")
    print("               FINAL HEALTH REPORT             ")
    print("================================================")
    for script, status in results.items():
        print(f"{Path(script).name:<45} [{status}]")
    print("================================================\n")

if __name__ == "__main__":
    run_diagnostics()
