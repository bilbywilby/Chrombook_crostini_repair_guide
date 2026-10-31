#!/usr/bin/env python3
"""
Procedure 3: Force Stop & Restart Container
Recovery procedure to force-terminate hung processes and reboot an LXD container.
"""
import subprocess
import sys
import time

def run_step(description: str, cmd: str):
    print(f"--> {description}")
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if res.stdout:
        print(res.stdout.strip())
    if res.returncode != 0 and res.stderr:
        print(f"Error: {res.stderr.strip()}", file=sys.stderr)

def restart_container(container_name="penguin"):
    print(f"=== SAFELY RESTARTING UNRESPONSIVE CONTAINER: {container_name} ===")
    run_step(f"Force-stopping container '{container_name}'...", f"lxc stop --force {container_name}")
    time.sleep(2)
    run_step("Verifying container power state...", "lxc list")
    run_step(f"Booting container '{container_name}'...", f"lxc start {container_name}")
    time.sleep(3)
    run_step("Verifying container responsiveness...", f"lxc exec {container_name} -- uptime")

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "penguin"
    restart_container(target)
