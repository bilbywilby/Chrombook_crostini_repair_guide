#!/usr/bin/env bash
# ==============================================================================
# Script Name: setup_crostini_repair.sh
# Description: Automates directory structure creation, unit tests, backup script
#              generation, and creates 5 standalone Python diagnostic scripts.
# ==============================================================================
set -euo pipefail

# Ensure we're in the repository root
REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || echo "$PWD")
cd "$REPO_ROOT"

echo "==> Creating project directory structure..."
mkdir -p tests
mkdir -p scripts
mkdir -p automation/procedures

# 1. Create tests/__init__.py and unit test suite
echo "==> Creating test suite..."
cat << 'EOF' > tests/__init__.py
# Test package initialization
EOF

cat << 'EOF' > tests/test_project_structure.py
import unittest
from pathlib import Path

class TestProjectStructure(unittest.TestCase):
    def test_readme_exists(self):
        """Verify that README.md exists in the repository root."""
        self.assertTrue(Path('README.md').exists(), "README.md is missing from root directory")

    def test_scripts_exist(self):
        """Verify that required automation scripts exist."""
        required_scripts = ['backup_runner.sh']
        for script in required_scripts:
            self.assertTrue(Path(f'scripts/{script}').exists(),
                          f'Missing script: scripts/{script}')

    def test_procedures_exist(self):
        """Verify that diagnostic procedures exist."""
        required_procedures = [
            '01_crosh_hypervisor_health_check.py',
            '02_lxd_container_health_check.py',
            '03_restart_unresponsive_container.py',
            '04_container_safety_snapshot.py',
            '05_list_container_snapshots.py'
        ]
        for proc in required_procedures:
            self.assertTrue(Path(f'automation/procedures/{proc}').exists(),
                          f'Missing procedure: automation/procedures/{proc}')

if __name__ == '__main__':
    unittest.main()
EOF

# 2. Create production-ready backup_runner.sh
echo "==> Creating backup script..."
cat << 'EOF' > scripts/backup_runner.sh
#!/usr/bin/env bash
set -euo pipefail

# Use absolute path for backup directory
BACKUP_DIR="$HOME/.cache/crostini_backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/workspace_$TIMESTAMP.tar.gz"

mkdir -p "$BACKUP_DIR"

if [ -d "$HOME/Linux" ]; then
    echo "Creating backup of $HOME/Linux..."
    tar -czf "$BACKUP_FILE" -C "$HOME" Linux/
    echo "Backup created successfully at: $BACKUP_FILE"
else
    echo "Warning: $HOME/Linux directory does not exist. Skipping backup."
    exit 1
fi
EOF

chmod +x scripts/backup_runner.sh

# 3. Generate Python diagnostic scripts
echo "==> Creating diagnostic procedures..."

# Procedure 1: Quick hypervisor health check
cat << 'PYEOF' > automation/procedures/01_crosh_hypervisor_health_check.py
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
PYEOF

# Procedure 2: LXD Container Health Check
cat << 'PYEOF' > automation/procedures/02_lxd_container_health_check.py
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
PYEOF

# Procedure 3: Force Stop & Restart Container
cat << 'PYEOF' > automation/procedures/03_restart_unresponsive_container.py
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
PYEOF

# Procedure 4: Container Safety Snapshot Manager
cat << 'PYEOF' > automation/procedures/04_container_safety_snapshot.py
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
PYEOF

# Procedure 5: List Container Snapshots
cat << 'PYEOF' > automation/procedures/05_list_container_snapshots.py
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
PYEOF

# Set execution permissions
chmod +x scripts/backup_runner.sh
chmod +x automation/procedures/*.py

# Run tests
echo "==> Running unit tests..."
python3 -m unittest discover -s tests -p "test_*.py" -v

# Stage and commit setup files
echo "==> Staging files for Git..."
git add tests/ scripts/ automation/

echo "==> Displaying repository status..."
git status

echo "==> Setup complete!"

