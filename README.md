CROSTINI REPAIR GUIDE — POWER USER SKILL
=====================================================

SKILL NAME: crostini-repair-guide
FOCUS: Top-down diagnosis (ChromeOS host → Termina VM → LXD container). Prioritizes hypervisor health, storage bottlenecks (virtio-9p vs native ext4), emergency recovery steps, partition safety, and secure port-forwarding.

TRIGGER PHRASES (ask any of these):
 * "My Crostini apps freeze or crash immediately"
 * "How do I safely expand the Linux disk on my Chromebook without data loss?"
 * "Termina VM not responding — force-stop or reset?"
 * "Port forwarding inside Crostini is too slow / insecure — what's the right way?"
 * "Linux environment won't start / keeps stopping after update"

────────────────────────────────────────────────────
1. HYPERVISOR HEALTH CHECK (5 seconds)
────────────────────────────────────────────────────

Open Crosh shell: `Ctrl+Alt+T`

```bash
# 1. Check VM state
vmc list

# 2. Force-stop if stuck in limbo
vmc stop --force termina
vmc start termina

# 3. Verify Termina is actually running
vmc status
```
*Red flag:* If `vmc` returns *"VM not found"* → Termina VM unprovisioned.  
Action: Settings → Linux → **Turn off Linux**, wait 10s, then **Turn on Linux**.

────────────────────────────────────────────────────
2. STORAGE & MEMORY BOTTLENECKS (quantified)
────────────────────────────────────────────────────

**Shared Mount (`~/Linux`) vs Native Container FS:**

| Metric              | virtio-9p shared mount | Native ext4 inside container |
|---------------------|--------------------------|------------------------------|
| Sequential Read     | ~40–60 MB/s             | ~250–300 MB/s              |
| Small-file IOPS     | ~1.5k ops/sec            | ~5k ops/sec                 |
| Large file copy     | ~3 GB/min                | ~8 GB/min                   |

**Impact:** Compiling large projects (`npm install`, `make`, `git clone`) in shared folders is up to **8× slower**. Keep source control and build artifacts within the container root (`/`).

────────────────────────────────────────────────────
3. SAFE DISK EXPANSION (non-destructive)
────────────────────────────────────────────────────

**Never resize while the container is running.** crosvm silently corrupts partitions otherwise.

Step-by-step:
```bash
# ChromeOS shell (Crosh)
# 1. Stop container gracefully
lxc stop <container_name>

# 2. Take snapshot (mandatory)
lxc snapshot <container_name> backup_$(date +%F)

# 3. Resize VM disk
vmc resize --disk-size=25G

# 4. Start container
lxc start <container_name>

# 5. Inside container, grow filesystem
lxc exec <container_name> -- growpart /dev/mmcblk0p1 1   # adjust device as needed
lxc exec <container_name> -- resize2fs /dev/mmcblk0p1    # ext4
```

⚠️ **Do NOT use `vmc resize` from inside the container.** It will fail or brick the VM.

────────────────────────────────────────────────────
4. 5-MINUTE EMERGENCY RECOVERY ROUTINE
────────────────────────────────────────────────────

When Linux apps refuse to launch or the terminal hangs:

1. **Hypervisor State**
   ```bash
   vmc list
   ```
   Is `terminia` RUNNING? If STOPPED → `vmc start termina`

2. **Force Clean Shutdown**
   ```bash
   vmc stop --force termina
   vmc start termina
   ```

3. **Kernel Logs (host)**
   ```bash
   dmesg | tail -50 | grep -E "(crosvm|virtio|oom)"
   ```
   Look for:
   - `Out of memory` → Container leaking RAM or exceeding allocated quota.
   - `Device not responding` → virtio driver drop.

4. **Isolated Container Test**
   ```bash
   lxc start penguin   # replace 'penguin' with your container name
   lxc exec penguin -- ping -c 2 10.0.2.2
   ```
   If pings work but apps still fail → app-specific config issue (PATH, systemd unit misconfiguration).

5. **Reset Last Resort**
   Settings → Linux → **Turn off Linux** → wait 10s → **Turn on Linux**

────────────────────────────────────────────────────
5. SECURE PORT FORWARDING (no sandbox bypass)
────────────────────────────────────────────────────

**Standard pattern everyone uses (bad):**
```bash
lxc exec <container> -- socat TCP-LISTEN:8080,fork,reuseaddr TCP:127.0.0.1:80
```
→ Exposes port across all interfaces including Wi-Fi unless explicitly blocked.

**Recommended pattern (safer):**
1. Use built-in ChromeOS port forwarding (Settings → Linux → Forward ports).
2. OR: Bind socat locally only:
   ```bash
   lxc exec <container> -- socat TCP-LISTEN:8080,fork,reuseaddr TCP:127.0.0.1:80
   ```
   Then manually whitelist that port on the ChromeOS host using its firewall:
   ```bash
   sudo iptables -A INPUT -p tcp --dport 8080 -j ACCEPT
   sudo iptables-save > /etc/iptables/rules.v4
   ```

**Security warning:** Binding to `0.0.0.0` inside the container bypasses ChromeOS sandboxing rules. On open networks, this can expose local development servers globally unless you scope the firewall above.

────────────────────────────────────────────────────
6. QUICK REFERENCE CHEAT SHEET
────────────────────────────────────────────────────

**Commands (run from Crosh shell)**:
```bash
vmc list          # VM state
vmc status        # Detailed stats
vmc stop --force  # Hard stop
vmc start         # Restart VM
lxc list          # Container state
lxc stop          # Stop container
lxc start         # Start container
lxc exec <name> -- <command>  # Run command inside container
lxc snapshot <name> backup_$(date +%F)  # Mandatory before resizing
```

**Performance baseline test (inside container):**
```bash
dd if=/dev/zero of=testfile bs=1M count=1024 conv=fdatasync status=progress && rm testfile
time find /usr/share -type f | wc -l
```

**Disk space check:**
```bash
df -h /  # Inside container
vmc list      # From Crosh to see VM disk usage
```

────────────────────────────────────────────────────
END OF SKILL
Use anytime you need to diagnose why Crostini feels sluggish, crashes, or refuses to start. Always begin at the host layer; containers are rarely the problem when ChromeOS itself throttles the hypervisor.
