#!/usr/bin/env python3
"""
Procedure 1: Quick Crosvm & Termina VM Health Check
Runs host-level diagnostics for Crostini (vmc list, ps aux for crosvm, dmesg, and vmc status).
"""
import subprocess
import sys

def run_cmd(cmd: str) -> str:
    print(f"--> Running: {cmd}")
    try:
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
        return res.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running command '{cmd}': {e.stderr}", file=sys.stderr)
        return ""

def hypervisor_health_check():
    print("=== CROSTINI HYPERVISOR HEALTH CHECK ===")
    print("\n1. Registered VMs (vmc list):")
    print(run_cmd("vmc list"))
    print("\n2. Active crosvm Processes:")
    print(run_cmd("ps aux | grep crosvm"))
    print("\n3. Kernel Ring Buffer Diagnostic Logs:")
    print(run_cmd("dmesg | tail -50 | grep -E '(crosvm|virtio|oom)' || echo 'No errors found.'"))
    print("\n4. Termina VM Status:")
    print(run_cmd("vmc status termina"))

if __name__ == "__main__":
    hypervisor_health_check()
