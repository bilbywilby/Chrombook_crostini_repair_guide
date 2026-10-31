# Diagnostic Tools

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
