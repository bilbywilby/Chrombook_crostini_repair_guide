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
