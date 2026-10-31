# Emergency Recovery

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
