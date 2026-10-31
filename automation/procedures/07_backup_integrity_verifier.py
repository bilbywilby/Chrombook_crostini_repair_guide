#!/usr/bin/env python3
import os
import time

BACKUP_DIR = os.path.expanduser("~/Linux/.backups")

def verify_backups():
    print("=== Backup Integrity Verifier ===")
    if not os.path.exists(BACKUP_DIR):
        print(f"[FAIL] Backup directory not found: {BACKUP_DIR}")
        return
    
    backups = [f for f in os.listdir(BACKUP_DIR) if f.endswith(('.tar.gz', '.tgz', '.tar'))]
    if not backups:
        print("[FAIL] No backup archives found.")
        return
    
    latest_backup = max([os.path.join(BACKUP_DIR, f) for f in backups], key=os.path.getmtime)
    size = os.path.getsize(latest_backup)
    mtime = os.path.getmtime(latest_backup)
    age_hours = (time.time() - mtime) / 3600
    
    print(f"Latest backup: {os.path.basename(latest_backup)}")
    print(f"Size: {size / (1024*1024):.2f} MB")
    print(f"Age: {age_hours:.1f} hours")
    
    if size == 0:
        print("[FAIL] Latest backup is empty (0 bytes).")
    elif age_hours > 48:
        print(f"[WARN] Backup is {age_hours:.1f} hours old.")
    else:
        print("[PASS] Backup exists, has content, and is recent.")

if __name__ == "__main__":
    verify_backups()
