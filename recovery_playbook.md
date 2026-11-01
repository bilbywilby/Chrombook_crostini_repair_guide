# Crostini Advanced Repair & Recovery Playbook

Maintained by bilbywilby (Tech Support Specialist)  
Environment: ChromeOS `termina` VM / LXD `penguin` container  

---

## 1. Storage Management & Disk Expansion
When encountering disk pressure or GPU buffer corruption:
1. **Clean Unused Assets**:
   ```bash
   docker system prune -a --volumes -f
   lxc image list && lxc image delete <fingerprint>
   sudo apt clean && sudo journalctl --vacuum-time=3d

