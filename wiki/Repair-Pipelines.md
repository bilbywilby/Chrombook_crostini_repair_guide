# Repair Pipelines

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
