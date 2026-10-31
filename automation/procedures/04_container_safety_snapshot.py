#!/usr/bin/env python3
"""
Procedure 4: Container Safety Snapshot
Creates a timestamped LXD snapshot and verifies registration before modifications.
"""
import subprocess
import sys
from datetime import datetime

def run_cmd(cmd: str):
    print(f"--> Running: {cmd}")
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if res.stdout:
        print(res.stdout.strip())
    if res.returncode != 0:
        print(f"Command failed: {res.stderr.strip()}", file=sys.stderr)
        sys.exit(1)

def create_snapshot(container_name="penguin"):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M")
    snapshot_name = f"backup_{timestamp}"
    print(f"=== CREATING SAFETY SNAPSHOT FOR '{container_name}' ===")
    print(f"Target Snapshot Name: {snapshot_name}")
    run_cmd(f"lxc snapshot {container_name} {snapshot_name}")
    print("\nVerifying Snapshot Registration:")
    run_cmd(f"lxc info {container_name}")

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "penguin"
    create_snapshot(target)
