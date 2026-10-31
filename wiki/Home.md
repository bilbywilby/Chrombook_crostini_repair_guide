# Crostini Repair Guide

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
