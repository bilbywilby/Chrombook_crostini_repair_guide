# CROSTINI REPAIR GUIDE — POWER USER FIELD MANUAL

**SKILL NAME:** `crostini-repair-guide`  
**PRIMARY ANGLE:** **Start at the host.** `crosvm` silently throttles or kills processes before your LXD container ever registers an error. 90% of "Linux is broken" issues are actually ChromeOS hypervisor limits or memory leaks.

---

## 1. Trigger Matrix & Intent Mapping

| User Query / Intent Pattern | Target Workflow / Action | Priority Layer |
| :--- | :--- | :--- |
| *"My Crostini apps crash instantly or freeze"* | `vmc list` → `dmesg \| grep oom` | Host (`crosvm`) |
| *"Disk full, no space left inside container"* | Stop container → Snapshot → `vmc resize` → `growpart` | VM + Container |
| *"Termina VM won't start / socket closed"* | Force-stop Termina VM and clean restart | VM (`Termina`) |
| *"Port forwarding inside Crostini is slow/insecure"* | Loopback binding inside container + `iptables` whitelist | Network / Host |
| *"Linux environment completely disappeared"* | Provisioning check → `Turn off Linux` → `Turn on Linux` | Host (`Crosh`) |

---

## 2. Layered Architecture

```text
┌─────────────────────────────────────────────────────────────┐
│ 1. ChromeOS Host System                                    │
│    - Kernel & Exo Compositor                                │
│    - Crosh Shell (`Ctrl+Alt+T` → `shell`)                  │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. crosvm Hypervisor Layer (Rust-based VMM)                 │
│    - Silent memory limits & VirtIO device mapping           │
│    - Process inspection: `ps aux | grep crosvm`            │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. Termina VM Layer (Minimal ChromeOS Linux)               │
│    - Managed via `vmc` (`start`, `stop`, `resize`)          │
│    - Internal DNS forwarder at `10.0.2.3`                   │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. LXD Container Layer ("penguin" / custom containers)      │
│    - Managed via `lxc` (`exec`, `snapshot`, `restore`)      │
│    - Native ext4 file system vs. virtio-9p shared mount     │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Hypervisor Health Check (30 Seconds)

Execute from the Crosh shell (`Ctrl+Alt+T` → `shell`):

```bash
# 1. Check VM state
vmc list

# 2. Force-stop if stuck in limbo
vmc stop --force termina

# 3. Restart Termina VM
vmc start termina

# 4. Verify running status
vmc status
```

> ⚠️ **Red Flag:** If `vmc` returns *"VM not found"*, the Termina VM has been unprovisioned.  
> **Action:** Navigate to **Settings** → **Linux** → **Turn off Linux**, wait 10 seconds, then **Turn on Linux**.

---

## 4. Safe Disk Expansion (Non-Destructive)

> ⛔ **CRITICAL WARNING:** Never run `vmc resize` while the container is actively writing, and never resize from inside the container. Partition table corruption is guaranteed.

### Step-by-Step Expansion Workflow:

```bash
# --- ChromeOS Shell (Crosh) ---

# 1. Gracefully halt the target container
lxc stop <container_name>

# 2. Create a mandatory safety snapshot
lxc snapshot <container_name> backup_$(date +%F)

# 3. Expand the VM block device allocation
vmc resize --disk-size=25G

# 4. Boot the container
lxc start <container_name>


# --- Inside LXD Container (via root exec) ---

# 5. Expand partition 1 on the virtual disk
lxc exec <container_name> -- growpart /dev/mmcblk0p1 1

# 6. Resize the file system (ext4)
lxc exec <container_name> -- resize2fs /dev/mmcblk0p1

# (For XFS filesystems, use this instead:)
# lxc exec <container_name> -- xfs_growfs /
```

---

## 5. Emergency Recovery Routine (When Linux Won't Launch)

Run this checklist sequentially when terminal windows hang or GUI apps fail to open:

1. **Verify Hypervisor State:**
   ```bash
   vmc list
   ```
   *If `termina` is `STOPPED`, launch it via `vmc start termina`.*

2. **Force Sever Corrupted VirtIO Sockets:**
   ```bash
   vmc stop --force termina
   vmc start termina
   ```

3. **Inspect Host Kernel Messages:**
   ```bash
   dmesg | tail -50 | grep -E "(crosvm|virtio|oom)"
   ```
   *Look for `Out of memory` (crosvm process kill) or `Device not responding` (virtio failure).*

4. **Isolated Container Reachability Test:**
   ```bash
   lxc start penguin
   lxc exec penguin -- ping -c 2 10.0.2.2
   ```
   *If ping succeeds, the issue is internal guest configuration (e.g., systemd unit failure, misconfigured `$PATH`, or broken X11 socket).*

---

## 6. Secure Port Forwarding Patterns

### The Vulnerable Pattern (Avoid):
```bash
# Binding socat to 0.0.0.0 inside the container bypasses ChromeOS sandboxing rules!
lxc exec <container> -- socat TCP-LISTEN:8080,fork,reuseaddr TCP:127.0.0.1:80
```
*Risk:* Exposes internal local development servers directly to untrusted Wi-Fi networks.

### Recommended Secure Pattern:

1. **Preferred Method:** Use native ChromeOS forwarding in **Settings** → **Linux** → **Forward ports**.
2. **Manual Loopback Binding:**
   ```bash
   # Bind strictly to loopback inside the container
   lxc exec <container_name> -- socat TCP-LISTEN:8080,bind=127.0.0.1,fork,reuseaddr TCP:127.0.0.1:80
   
   # Whitelist explicitly on the host firewall (Crosh)
   sudo iptables -A INPUT -p tcp --dport 8080 -j ACCEPT
   sudo iptables-save > /etc/iptables/rules.v4
   ```

---

## 7. Performance Benchmarks (`virtio-9p` vs. Native `ext4`)

Shared folders mapped from ChromeOS (`~/Linux` or `MyFiles`) utilize `virtio-9p`. Keep all build artifacts, `node_modules`, and Git repositories inside the native container file system (`/home/user/`).

$$\begin{array}{|l|c|c|}
\hline
\textbf{Metric} & \textbf{virtio-9p Shared Mount (\text{\sim}/Linux)} & \textbf{Native ext4 Container Storage} \\ \hline
\text{Sequential Read} & \sim 40\text{--}60\text{ MB/s} & \sim 250\text{--}300\text{ MB/s} \\ \hline
\text{Small-File IOPS} & \sim 1,500\text{ ops/sec} & \sim 5,000\text{ ops/sec} \\ \hline
\text{Large File Copy} & \sim 3\text{ GB/min} & \sim 8\text{ GB/min} \\ \hline
\text{Compilation Impact} & \mathbf{Up\ to\ 8\times\ slower} & \mathbf{Baseline\ Speed} \\ \hline
\end{array}$$

### Baseline Performance Test Commands (Run Inside Container):
```bash
# Test write throughput
dd if=/dev/zero of=testfile bs=1M count=1024 conv=fdatasync status=progress && rm testfile

# Test small-file I/O latency
time find /usr/share -type f | wc -l
```

---

## 8. Quick Reference Command Cheat Sheet

### Host Commands (Crosh Shell):
```bash
vmc list                              # List active virtual machines
vmc status                            # Display memory usage & status
vmc stop --force termina              # Hard kill Termina VM
vmc start termina                     # Boot Termina VM
```

### LXD Container Commands (Crosh / Termina):
```bash
lxc list                              # List container status and IP addresses
lxc stop <container>                  # Graceful container shutdown
lxc start <container>                 # Start container
lxc exec <container> -- <cmd>         # Execute command inside container
lxc snapshot <container> <snap_name>  # Create full point-in-time snapshot
lxc restore <container> <snap_name>   # Roll back to snapshot
```

---

## 9. Nuclear Escalation Path (Ordered by Destructiveness)

1. **Restart Container:** `lxc restart <container_name>`
2. **Force-Restart Hypervisor:** `vmc stop --force termina && vmc start termina`
3. **Reset Linux Environment (Keeps user files):** Settings → Linux → **Reset Linux**
4. **Deprovision Linux (Destroys container & VM):** Settings → Linux → **Turn off Linux**
5. **Chromebook Powerwash (Wipes entire device):** Settings → Device → **Erase**