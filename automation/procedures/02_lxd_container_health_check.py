#!/usr/bin/env python3
"""
Procedure 2: LXD Container Health Check
Inspects active containers, resource limits, systemd service health, and network latency.
"""
import subprocess
import sys

def run_container_cmd(cmd: str):
    print(f"--> Running: {cmd}")
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if res.stdout:
        print(res.stdout.strip())
    if res.stderr:
        print(f"Notice: {res.stderr.strip()}", file=sys.stderr)

def lxd_health_check(container_name="penguin"):
    print(f"=== LXD CONTAINER HEALTH CHECK: {container_name} ===")
    print("\n1. Active Container States:")
    run_container_cmd("lxc list")
    print(f"\n2. Container Detailed Info ({container_name}):")
    run_container_cmd(f"lxc info {container_name}")
    print(f"\n3. Systemd Unit Failures ({container_name}):")
    run_container_cmd(f"lxc exec {container_name} -- systemctl --failed")
    print(f"\n4. Internal Gateway Network Latency Check:")
    run_container_cmd(f"lxc exec {container_name} -- ping -c 2 10.0.2.2")

if __name__ == "__main__":
    container = sys.argv[1] if len(sys.argv) > 1 else "penguin"
    lxd_health_check(container)
