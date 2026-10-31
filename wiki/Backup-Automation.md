# Backup Automation

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
