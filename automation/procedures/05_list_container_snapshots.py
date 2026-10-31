#!/usr/bin/env python3
"""
Procedure 5: List Container Snapshots
Lists registered LXD container snapshots and displays associated timestamps.
"""
import subprocess
import sys

def list_snapshots(container_name="penguin"):
    print(f"=== LISTING SNAPSHOTS FOR CONTAINER: {container_name} ===")
    cmd = f"lxc info {container_name}"
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"Error querying container '{container_name}': {res.stderr.strip()}", file=sys.stderr)
        sys.exit(1)

    output_lines = res.stdout.splitlines()
    in_snapshots = False
    snapshots_found = []

    for line in output_lines:
        if line.strip().startswith("Snapshots:"):
            in_snapshots = True
            continue
        if in_snapshots:
            if line.startswith("  ") and not line.startswith("    "):
                snapshots_found.append(line.strip())
            elif not line.startswith(" "):
                break

    if snapshots_found:
        print(f"\nFound {len(snapshots_found)} snapshot(s):")
        for snap in snapshots_found:
            print(f"  - {snap}")
    else:
        print("\nNo snapshots currently registered for this container.")

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "penguin"
    list_snapshots(target)
