#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

cat > Diagnostic-Tools.md <<'MD_DIAG'
# Diagnostic Tools & Scripts

**Execution context: LXD container or Termux shell.** None of these run from crosh.

## 1. Master Diagnostic Script

**File:** `crostini_master_diagnostic.py`

Performs automated multi-layer health checks across hypervisor state, container
status, and disk allocation — evaluating `termina`/`vmc` state, `ext4` mount
health, and `lxc list` output.

```bash
python3 crostini_master_diagnostic.py
