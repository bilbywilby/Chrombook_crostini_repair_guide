#!/usr/bin/env bash
set -Eeuo pipefail

BACKUP_DIR="${HOME}/Linux/.backups"
SOURCE_DIR="${HOME}/Linux"
LOG_FILE="${HOME}/.cache/crostini_backup.log"

mkdir -p "$BACKUP_DIR" "$(dirname "$LOG_FILE")"

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
ARCHIVE_NAME="crostini_backup_${TIMESTAMP}.tar.gz"
DEST_PATH="$BACKUP_DIR/$ARCHIVE_NAME"

echo "[INFO] Starting backup of $SOURCE_DIR to $DEST_PATH" | tee -a "$LOG_FILE"
tar -czf "$DEST_PATH" -C "$(dirname "$SOURCE_DIR")" "$(basename "$SOURCE_DIR")" --exclude=".backups" 2>> "$LOG_FILE"

# Verify archive size
if [ -s "$DEST_PATH" ]; then
    echo "[PASS] Backup created successfully: $(du -sh "$DEST_PATH" | cut -f1)" | tee -a "$LOG_FILE"
else
    echo "[ERROR] Backup archive is empty or failed." | tee -a "$LOG_FILE"
    exit 1
fi

# GFS Retention Pruning (Prune archives older than 90 days)
find "$BACKUP_DIR" -name "crostini_backup_*.tar.gz" -mtime +90 -delete
