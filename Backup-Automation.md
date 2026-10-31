# Backup & Workspace Automation

**Execution context: container shell.**

## Repository Synchronization

**Script:** `automation/sync_crostini_repo.sh`

Stashes uncommitted changes and performs fast-forward pulls (`git pull --ff-only`).

## GFS Backup Runner

**Script:** `automation/backup_runner.sh`

Compresses workspaces into `.tar.gz` archives with GFS retention pruning.

## Systemd Automation

```bash
systemctl --user enable crostini-backup.timer
systemctl --user start crostini-backup.timer
