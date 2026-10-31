import os
import time

BACKUP_DIR = os.path.expanduser("~/Linux/.backups")
MAX_AGE_SECONDS = 72 * 3600  # 72 hours

def verify_backup_integrity():
    print("=== Backup Integrity & Staleness Verifier ===")
    if not os.path.exists(BACKUP_DIR):
        print(f"[FAIL] Backup directory not found: {BACKUP_DIR}")
        return False
    
    archives = [os.path.join(BACKUP_DIR, f) for f in os.listdir(BACKUP_DIR) if f.endswith(".tar.gz")]
    if not archives:
        print(f"[FAIL] No backup archives found in {BACKUP_DIR}")
        return False
    
    newest = max(archives, key=os.path.getmtime)
    age = time.time() - os.path.getmtime(newest)
    
    if age > MAX_AGE_SECONDS:
        print(f"[FAIL] Newest backup is stale ({age / 3600:.1f} hours old, max allowed: 72h)")
        return False
    
    print(f"[PASS] Newest backup is current ({age / 3600:.1f} hours old)")
    return True

if __name__ == "__main__":
    success = verify_backup_integrity()
    exit(0 if success else 1)
