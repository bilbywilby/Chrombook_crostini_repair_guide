#!/usr/bin/env python3
"""Build, validate, and package the Crostini Repair Guide wiki pages."""

from __future__ import annotations

import hashlib
import os
import re
import stat
import sys
import tarfile
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
WIKI_DIR = ROOT / "wiki"
TARBALL = ROOT / "crostini-repair-guide-wiki.tar.gz"
GITIGNORE = ROOT / ".gitignore"

WIKI_FILES: dict[str, str] = {
    "Home.md": """# Crostini Repair Guide

This wiki documents diagnostic and recovery procedures for ChromeOS Linux (Crostini), including the ChromeOS host, the Termina virtual machine, and its LXD container.

## Pages

- [[Architecture-Overview|Architecture overview]]
- [[Diagnostic-Tools|Diagnostic tools]]
- [[Repair-Pipelines|Repair pipelines]]
- [[Test-Suite-Reference|Test suite reference]]
- [[Backup-Automation|Backup automation]]
- [[Emergency-Recovery|Emergency recovery]]

## Execution contexts

Commands run in different environments. `vmc` commands belong in the ChromeOS crosh shell. Container and Python diagnostics should be run in the environment specified by the procedure, such as the LXD container or Termux. Check each procedure's prerequisites before running commands.
""",

    "Architecture-Overview.md": """# Architecture Overview

Crostini troubleshooting is easiest when performed from the outer layer inward:

1. **ChromeOS host:** Check host-level state and use crosh for `vmc` operations.
2. **Termina VM:** Check whether the Linux virtual machine is running and reachable.
3. **LXD container:** Check container state, Linux services, storage, and project diagnostics.

A failure at an outer layer can make inner-layer checks misleading. Establish which layer is responding before changing configuration.

## Resource guidance

The project resource-allocation guidance recommends allocating Termina RAM at approximately 50% of physical RAM and using 35 GB as a recommended LXD disk size. Treat these as starting recommendations, not universal requirements; available host resources and workload needs vary.

## Command boundaries

- Run `vmc` commands from ChromeOS crosh, not from the Linux container.
- Run `lxc` and the Python diagnostic procedures in their documented Linux environment.
- Review the effect of any shutdown, resize, or migration operation before proceeding.
""",

    "Diagnostic-Tools.md": """# Diagnostic Tools

The repository includes shell and Python tools for collecting diagnostic information.

## Diagnostic sequence

Use a top-down sequence:

1. Check ChromeOS and crosh-level VM state.
2. Check Termina VM health and resource availability.
3. Check LXD container state and Linux services.
4. Run the repository's focused diagnostic procedures.

The procedures `01_crosh_hypervisor_health_check.py` through `09_vm_resource_profiler.py` provide individual checks. `crostini_master_diagnostic.py` runs the diagnostic procedures sequentially. Review the output before attempting repairs.

## Log-source fallback

When investigating system logs, try the available sources in this order:

1. `dmesg`
2. `journalctl`
3. `/var/log/syslog`

Availability and permissions differ between environments. A missing source does not by itself establish that the system is healthy or unhealthy.

## Hypervisor diagnostics

`crosvm_diagnostics.sh` collects hypervisor-related information. Run it only in its documented execution context, and treat collected diagnostic output as potentially sensitive before sharing it.
""",

    "Repair-Pipelines.md": """# Repair Pipelines

Use the least disruptive checks first. Save work before any operation that stops a VM or container.

## VM unresponsive

1. Open ChromeOS crosh with `Ctrl+Alt+T`.
2. Check VM state with:
   ```bash
   vmc list
   ```
3. Review the diagnostic output and confirm that you intend to stop the VM before running:
   ```bash
   vmc stop termina
   ```

> **Warning:** `vmc stop termina` stops the underlying Termina VM and terminates running container processes and active sessions. Save work first.

4. After the VM is available again, check container state and run the relevant diagnostics from their documented environment.

## Storage pressure

1. Check available space inside the affected Linux environment:
   ```bash
   df -h /
   ```
2. Identify large files or directories before deleting anything.
3. If a VM disk resize is needed, use the documented `vmc resize` procedure from crosh and select a size appropriate for the device.
4. Recheck available space after the operation.

Avoid deleting files or changing filesystem layouts without a verified backup and a procedure that matches the affected environment.
""",

    "Test-Suite-Reference.md": """# Test Suite Reference

The repository test suite checks project structure and selected repository behavior.

## Run tests

From the repository root, run:

```bash
python3 -m unittest discover -s tests -v
```

If the project dependencies are required, install the pinned packages listed in `requirements.txt` in the intended Python environment before running tests.

## CI

The Python CI workflow tests the supported Python versions configured in the workflow. A local pass is useful, but CI may expose differences between Python versions or environments.

## Before committing

- Run the test suite from the repository root.
- Review `git status` and `git diff`.
- Do not commit generated reports or runtime files unless they are intended project artifacts.
""",

    "Backup-Automation.md": """# Backup Automation

The repository provides a backup runner for `~/Linux` and systemd user service and timer definitions for scheduled backups.

## Backup location and verification

The backup workflow provisions `~/Linux/.backups` when needed and uses a 72-hour staleness check to identify backups that may need attention. Review the backup runner's output and confirm the expected archive exists after a run.

## Run and inspect

Use the repository's documented setup for the systemd user service and timer. Check the service and timer status with:

```bash
systemctl --user status crostini-backup.service
systemctl --user status crostini-backup.timer
```

A successful service exit does not replace checking that the backup artifact is present and usable. Keep backup contents and logs protected, especially if they contain personal files.
""",

    "Emergency-Recovery.md": """# Emergency Recovery

Use this page as a cautious starting point when Crostini is unavailable. Follow the procedure for the affected layer and avoid destructive changes until important data is backed up.

## Initial checks

1. Save work in any still-responsive applications.
2. Determine whether the problem is at the ChromeOS host, Termina VM, or LXD container layer.
3. Use the matching checks in [[Diagnostic-Tools|Diagnostic Tools]].
4. Review available logs using the fallback order documented there.

## Before restarting Termina

`vmc stop termina` stops the Termina VM and terminates running container processes and active sessions. Save work and confirm that a restart is appropriate before using it.

## Data and storage

- Do not delete container data or resize storage as an exploratory step.
- Confirm that a recent backup exists before attempting recovery that could affect stored data.
- Use the repository repair procedures that match the specific failure and execution context.
""",

    "_Sidebar.md": """## Crostini Repair Guide

- [[Home]]
- [[Architecture-Overview|Architecture overview]]
- [[Diagnostic-Tools|Diagnostic tools]]
- [[Repair-Pipelines|Repair pipelines]]
- [[Test-Suite-Reference|Test suite reference]]
- [[Backup-Automation|Backup automation]]
- [[Emergency-Recovery|Emergency recovery]]
""",
}

REQUIRED_FILES = {
    "Home.md",
    "Architecture-Overview.md",
    "Diagnostic-Tools.md",
    "Repair-Pipelines.md",
    "Test-Suite-Reference.md",
    "Backup-Automation.md",
    "Emergency-Recovery.md",
    "_Sidebar.md",
}

WIKI_LINK_PATTERN = re.compile(r"\[\[([^\]|#]+)")


def atomic_write_text(path: Path, text: str) -> None:
    """Write text through a same-directory temporary file, then replace."""
    if path.is_symlink():
        raise OSError(f"Refusing to replace symlink: {path}")

    mode = stat.S_IMODE(path.stat().st_mode) if path.exists() else 0o644
    fd, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.",
        suffix=".tmp",
        dir=path.parent,
    )
    temporary_path = Path(temporary_name)

    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())

        os.chmod(temporary_path, mode)
        os.replace(temporary_path, path)
    finally:
        temporary_path.unlink(missing_ok=True)


def validate_wiki_links() -> None:
    """Check that each [[Page]] reference names a generated wiki page."""
    missing_files = REQUIRED_FILES - set(WIKI_FILES)
    if missing_files:
        names = ", ".join(sorted(missing_files))
        raise ValueError(f"Required wiki page definitions are missing: {names}")

    available_pages = {
        Path(filename).stem
        for filename in WIKI_FILES
        if filename != "_Sidebar.md"
    }
    errors: list[str] = []

    for filename, content in WIKI_FILES.items():
        for raw_target in WIKI_LINK_PATTERN.findall(content):
            target = raw_target.strip()
            if target not in available_pages:
                errors.append(
                    f"{filename}: link target {target!r} has no generated page"
                )

    if errors:
        raise ValueError("Wiki link validation failed:\n" + "\n".join(errors))


def update_gitignore() -> None:
    """Add required runtime exclusions without duplicating existing lines."""
    if GITIGNORE.is_symlink():
        raise OSError(f"Refusing to update symlink: {GITIGNORE}")

    current = GITIGNORE.read_text(encoding="utf-8") if GITIGNORE.exists() else ""
    existing = {
        line.strip()
        for line in current.splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }
    required = ("FETCH_HEAD", "manifest_report.json")
    additions = [entry for entry in required if entry not in existing]

    if not additions:
        print("[*] .gitignore already contains the required exclusions.")
        return

    updated = current
    if updated and not updated.endswith("\n"):
        updated += "\n"
    updated += "".join(f"{entry}\n" for entry in additions)
    atomic_write_text(GITIGNORE, updated)
    print(f"[+] Added to .gitignore: {', '.join(additions)}")


def build_wiki() -> list[Path]:
    """Write all configured wiki pages and return their paths."""
    if WIKI_DIR.is_symlink():
        raise OSError(f"Refusing to write through symlink: {WIKI_DIR}")

    WIKI_DIR.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []

    for filename, content in WIKI_FILES.items():
        path = WIKI_DIR / filename
        page_text = content.strip() + "\n"
        atomic_write_text(path, page_text)
        written.append(path)
        print(f"[+] Wrote {path.relative_to(ROOT)}")

    return written


def create_tarball(files: list[Path]) -> str:
    """Create a temporary archive, replace the destination, and return its hash."""
    if TARBALL.is_symlink():
        raise OSError(f"Refusing to replace symlink: {TARBALL}")

    fd, temporary_name = tempfile.mkstemp(
        prefix=f".{TARBALL.name}.",
        suffix=".tmp",
        dir=ROOT,
    )
    os.close(fd)
    temporary_path = Path(temporary_name)

    try:
        with tarfile.open(temporary_path, mode="w:gz") as archive:
            for path in sorted(files, key=lambda item: item.name):
                if path.is_symlink() or not path.is_file():
                    raise OSError(f"Refusing to archive non-regular file: {path}")
                archive.add(path, arcname=f"wiki/{path.name}", recursive=False)

        os.replace(temporary_path, TARBALL)
    finally:
        temporary_path.unlink(missing_ok=True)

    digest = hashlib.sha256()
    with TARBALL.open("rb") as archive_file:
        for chunk in iter(lambda: archive_file.read(1024 * 1024), b""):
            digest.update(chunk)

    result = digest.hexdigest()
    print(f"[+] Created {TARBALL.name}")
    print(f"[+] SHA-256: {result}")
    return result


def main() -> int:
    print("=== Crostini Repair Guide Wiki Builder ===")
    validate_wiki_links()
    print("[+] Wiki link validation passed.")

    update_gitignore()
    files = build_wiki()
    create_tarball(files)

    print("=== Build complete ===")
    print(
        "[!] If FETCH_HEAD or manifest_report.json is already tracked, "
        "remove it from the Git index separately."
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, tarfile.TarError) as exc:
        print(f"build_wiki.py: error: {exc}", file=sys.stderr)
        raise SystemExit(1)
