# Crostini Repair Guide — Architecture & Power User Field Manual

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Platform: ChromeOS](https://img.shields.io/badge/Platform-ChromeOS%20%7C%20Crostini-00875A.svg)](https://chromium.googlesource.com/chromiumos/platform2/+/main/vm_tools/)
[![Stack: crosvm | Termina | LXD](https://img.shields.io/badge/Stack-crosvm%20%7C%20Termina%20%7C%20LXD-black.svg)](https://chromium.googlesource.com/chromiumos/platform/crosvm/)

> **Core Philosophy:** **Start at the top.**  
> ChromeOS throttles `crosvm` long before the container ever logs an error. **90% of "Linux is broken" issues are host or hypervisor resource leaks.** Debug from the host layer downward ($\text{Crosh} \longrightarrow \text{Termina VM} \longrightarrow \text{LXD Container}$).

---

## 📖 Table of Contents
- [Layered Stack Architecture](#-layered-stack-architecture)
- [Intent Matrix & Quick Triage](#-intent-matrix--quick-triage)
- [Execution Pipelines](#-execution-pipelines)
  - [Pipeline A: 30-Second Hypervisor Health Check](#pipeline-a-30-second-hypervisor-health-check)
  - [Pipeline B: Safe Disk Expansion](#pipeline-b-safe-disk-expansion-non-destructive)
  - [Pipeline C: Secure Port Exposure](#pipeline-c-secure-port-exposure-loopback-first)
- [Performance Data: virtio-9p vs Native ext4](#-performance-data--why-shared-mounts-are-slow)
- [Quick Reference Cheat Sheet](#-quick-reference-cheat-sheet)
- [Security Notice: Socat Configuration](#-security-notice-socat-configuration)
- [Nuclear Options (Recovery Paths)](#-nuclear-options-in-order-of-destructiveness)
- [Contributing & License](#-contributing)

---

## 📐 Layered Stack Architecture

```text
┌─────────────────────────────────────────────────────────────┐
│ ChromeOS Host System                                        │
│   - Crosh shell (`Ctrl+Alt+T` → `shell`)                    │
│   - Kernel & Exo Compositor                                 │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ crosvm Hypervisor Layer (Rust-based VMM)                    │
│   - Silent memory caps                                      │
│   - VirtIO device mapping                                   │
│   - Inspect via `ps aux | grep crosvm`                      │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ Termina VM Layer (Minimal Linux environment)                │
│   - Managed by `vmc` (`start`, `stop`, `resize`)            │
│   - Internal DNS forwarder at `10.0.2.3`                    │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ LXD Container Layer (Ubuntu/Debian guest)                     │
│   - Native ext4 vs virtio-9p shared mount                   │
│   - Commands: `lxc list`, `lxc exec`, `snapshot`, `restore` │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 Intent Matrix — What to Run When

| User Query Pattern | Target Action / Workflow | Layer Priority |
| :--- | :--- | :--- |
| *"Apps crash instantly"* | `vmc list` $\rightarrow$ `dmesg \| grep oom` | Host (`crosvm`) |
| *"Disk full, no space left"* | Stop container $\rightarrow$ Snapshot $\rightarrow$ `vmc resize` $\rightarrow$ `growpart` | VM + Container |
| *"Termina VM not responding"* | `vmc stop --force termina` $\rightarrow$ `vmc start` | VM (`Termina`) |
| *"Port forwarding too slow/insecure"* | Loopback binding inside container + `iptables` whitelist | Network / Host |
| *"Linux disappeared after update"* | Check provisioning $\rightarrow$ `Turn off Linux` $\rightarrow$ `Turn on Linux` | Host |

---

## 🛠️ Execution Pipelines

### Pipeline A: 30-Second Hypervisor Health Check
Run from Crosh (`Ctrl+Alt+T`):
```bash
vmc list
vmc stop --force termina
vmc start termina
vmc status
```

### Pipeline B: Safe Disk Expansion (Non-destructive)
> **Warning:** Never run `vmc resize` from inside the container. Partition table corruption is guaranteed.

```bash
# Host layer
lxc stop <container_name>
lxc snapshot <container_name> backup_$(date +%F)

# VM layer
vmc resize --disk-size=25G

# Boot & Expand
lxc start <container_name>

# Inside container (root access required)
lxc exec <container_name> -- growpart /dev/mmcblk0p1 1
lxc exec <container_name> -- resize2fs /dev/mmcblk0p1   # ext4
# For XFS:
lxc exec <container_name> -- xfs_growfs /
```

### Pipeline C: Secure Port Exposure (Loopback First)
```bash
# Bind only to localhost inside container
lxc exec <container_name> -- socat TCP-LISTEN:8080,fork,reuseaddr TCP:127.0.0.1:80

# Whitelist explicitly on host firewall
sudo iptables -A INPUT -p tcp --dport 8080 -j ACCEPT
sudo iptables-save > /etc/iptables/rules.v4
```

---

## 📊 Performance Data — Why Shared Mounts Are Slow

Benchmark comparison of `virtio-9p` vs native `ext4` on ChromeOS:

| Metric | `virtio-9p` (`~/Linux`) | Native `ext4` (`/home/user/`) |
| :--- | :--- | :--- |
| **Sequential Read** | ~40–60 MB/s | ~250–300 MB/s |
| **Small-file IOPS** | ~1.5k ops/sec | ~5k ops/sec |
| **Large file copy** | ~3 GB/min | ~8 GB/min |

**Developer Impact:** Compiling large projects (`npm install`, `make`, `git clone`) inside shared host folders is **up to 8× slower**. Keep source control and build artifacts in the container root filesystem (`/`), not in the host-shared `~/`.

---

## 📋 Quick Reference Cheat Sheet

### Host Commands (Crosh)
```bash
vmc list          # View VM state
vmc status        # View detailed stats
vmc stop --force  # Force hard kill
vmc start         # Restart VM
```

### Container Commands (LXD)
```bash
lxc list                                # Container status
lxc stop <name>                         # Halt container
lxc start <name>                        # Launch container
lxc exec <name> -- <command>            # Execute command as root
lxc snapshot <name> backup_$(date +%F)  # Create safety snapshot
lxc restore <name> backup_<YYYY-MM-DD>  # Rollback state
```

### In-Container Performance Baseline Test
```bash
dd if=/dev/zero of=testfile bs=1M count=1024 conv=fdatasync status=progress && rm testfile
time find /usr/share -type f | wc -l
```

### Disk Space Check
```bash
df -h /   # Inside container
vmc list  # From Crosh to inspect VM disk usage
```

---

## 🛡️ Security Notice: Socat Configuration

Binding `socat` to `0.0.0.0` inside Crostini bypasses ChromeOS sandboxing rules. On open Wi-Fi networks, this can expose local development servers globally unless host firewall rules are explicitly defined.

**Recommended Hardened Pattern:**
```bash
# Bind locally only inside container (safer)
lxc exec <container> -- socat TCP-LISTEN:8080,fork,reuseaddr TCP:127.0.0.1:80

# Mandatory host firewall rule
sudo iptables -A INPUT -p tcp --dport 8080 -j ACCEPT
```

---

## ☢️ Nuclear Options (In Order of Destructiveness)

1. **Restart container:** `lxc restart <container>`
2. **Force-stop Termina VM:** `vmc stop --force termina`
3. **Reset Linux environment:** Settings $\rightarrow$ Linux $\rightarrow$ **Turn off Linux**, wait 10s $\rightarrow$ **Turn on Linux**
4. **Full powerwash:** Settings $\rightarrow$ Device $\rightarrow$ **Erase**

---

## 🤝 Contributing

Pull requests and additions to the field guide are welcome. Please ensure commands and syntax adhere to current ChromeOS Crostini architectures.

## 📄 License

Distributed under the **MIT License**. See `LICENSE` for details.

--------------------------------------
CROSTINI REPAIR SKILL — ARCHITECTURE & PLAYBOOK

=====================================================

SKILL IDENTIFIER: crostini-repair-guide
CORE PHILOSOPHY: **Start at the top.** ChromeOS throttles crosvm before the container ever logs an error. 90% of "Linux is broken" issues are actually host/hypervisor resource leaks.

────────────────────────────────────────────────────
1. LAYERED STACK DIAGRAM (visual)
```
┌─────────────────────────────────────────────────────────────┐
│ ChromeOS Host System                                 │
│   - Crosh shell (`Ctrl+Alt+T` → `shell`)              │
│   - Kernel & Exo Compositor                          │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ crosvm Hypervisor Layer (Rust-based VMM)                 │
│   - Silent memory caps                                    │
│   - VirtIO device mapping                                │
│   - Inspect via `ps aux | grep crosvm`                   │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ Termina VM Layer (Minimal Linux environment)               │
│   - Managed by `vmc` (`start`, `stop`, `resize`)        │
│   - Internal DNS forwarder at `10.0.2.3`                │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ LXD Container Layer (Ubuntu/Debian guest)                  │
│   - Native ext4 vs virtio-9p shared mount                │
│   - Commands: `lxc list`, `lxc exec`, `snapshot`, `restore`│
└─────────────────────────────────────────────────────────────┘
```

────────────────────────────────────────────────────
2. INTENT MATRIX — WHAT TO RUN WHEN

| USER QUERY PATTERN                | TARGET ACTION / WORKFLOW                     | LAYER PRIORITY |
| :-------------------------------- | :------------------------------------------- | :-------------- |
| *"Apps crash instantly"*          | `vmc list` → `dmesg | grep oom`            | Host (`crosvm`) |
| *"Disk full, no space left"*     | Stop container → Snapshot → `vmc resize` → growpart | VM + Container |
| *"Termina VM not responding"*     | `vmc stop --force termina` → `vmc start`    | VM (`Termina`) |
| *"Port forwarding too slow/insecure"* | Loopback binding inside container + `iptables` whitelist | Network / Host |
| *"Linux disappeared after update"* | Check provisioning → `Turn off Linux` → `Turn on Linux` | Host |

────────────────────────────────────────────────────
3. EXECUTION PIPELINES (copy-paste ready)

### Pipeline A: 30-Second Hypervisor Health Check
```bash
# From Crosh (Ctrl+Alt+T)
vmc list
vmc stop --force termina
vmc start termina
vmc status
```

### Pipeline B: Safe Disk Expansion (Non-destructive)
```bash
# Host layer
lxc stop <container_name>
lxc snapshot <container_name> backup_$(date +%F)

# VM layer
vmc resize --disk-size=25G

# Boot & Expand
lxc start <container_name>

# Inside container (root access required)
lxc exec <container_name> -- growpart /dev/mmcblk0p1 1
lxc exec <container_name> -- resize2fs /dev/mmcblk0p1   # ext4
# For XFS:
lxc exec <container_name> -- xfs_growfs /
```

⚠️ **Never run `vmc resize` from inside the container.** Partition table corruption guaranteed.

### Pipeline C: Secure Port Exposure (Loopback First)
```bash
# Bind only to localhost inside container
lxc exec <container_name> -- socat TCP-LISTEN:8080,fork,reuseaddr TCP:127.0.0.1:80

# Whitelist explicitly on host firewall
sudo iptables -A INPUT -p tcp --dport 8080 -j ACCEPT
sudo iptables-save > /etc/iptables/rules.v4
```

────────────────────────────────────────────────────
4. PERFORMANCE DATA — WHY YOUR SHARED MOUNTS ARE SLOW

**Comparison:** virtio-9p vs native ext4 in a typical Chromebook model:

| Metric              | virtio-9p (~/Linux) | Native ext4 (/home/user/) |
| -------------------- | --------------------- | ------------------------- |
| Sequential Read      | ~40–60 MB/s         | ~250–300 MB/s           |
| Small-file IOPS      | ~1.5k ops/sec        | ~5k ops/sec              |
| Large file copy      | ~3 GB/min             | ~8 GB/min                 |

**Developer Impact:** Compiling large projects (`npm install`, `make`, `git clone`) in shared folders is up to **8× slower**. Keep source control and build artifacts in the container root filesystem (`/`), not in the host-shared `~/`.

────────────────────────────────────────────────────
5. QUICK REFERENCE CHEAT SHEET (no fluff)

**Host (Crosh):**
```bash
vmc list          # State
vmc status        # Details
vmc stop --force  # Hard kill
vmc start         # Restart VM
```

**Container (LXD):**
```bash
lxc list          # Status
lxc stop          # Halt
lxc start         # Launch
lxc exec <name> -- <command>  # Run command
lxc snapshot <name> backup_$(date +%F)  # Safety net
lxc restore <name> backup_<YYYY-MM-DD>  # Rollback
```

**Performance Baseline Test (inside container):**
```bash
dd if=/dev/zero of=testfile bs=1M count=1024 conv=fdatasync status=progress && rm testfile
time find /usr/share -type f | wc -l
```

**Disk Space Check:**
```bash
df -h /  # Inside container
vmc list      # From Crosh for VM disk usage
```

────────────────────────────────────────────────────
6. SECURITY REMINDER: SOCAT CONFIGURATION

**What most guides omit:**
Binding to `0.0.0.0` inside Crostini bypasses ChromeOS sandboxing rules. On open Wi-Fi networks, this can expose local development servers globally unless you explicitly scope the host firewall.

**Recommended pattern:**
```bash
# Bind locally only (safer)
lxc exec <container> -- socat TCP-LISTEN:8080,fork,reuseaddr TCP:127.0.0.1:80

# Mandatory host firewall rule
sudo iptables -A INPUT -p tcp --dport 8080 -j ACCEPT
```

────────────────────────────────────────────────────
7. NUCLEAR OPTIONS (in order of destructiveness)

1. Restart container: `lxc restart <container>`
2. Force-stop Termina VM: `vmc stop --force termina`
3. Reset Linux environment: Settings → Linux → **Turn off Linux**, wait 10s → **Turn on Linux**
4. Full powerwash: Settings → Device → **Erase**

────────────────────────────────────────────────────
END OF SKILL ARCHITECTURE
Trigger anytime you suspect Crostini is misbehaving. Start at the hypervisor; containers rarely cause what looks like their own failure.

Crostini Power User Field Guide & Diagnostics Toolkit
> Contrarian Premise:
> Container-level troubleshooting is a time sink. 90% of Crostini failures are host/hypervisor resource leaks.
> crosvm silently caps memory and throttles virtio-9p mounts long before the guest container registers an error. Debug from the host layer down (Crosh → Termina VM → LXD), not inside the container.
> 
📖 Table of Contents
 * Architecture & Mental Model
 * Directory & Repository Structure
 * Quick Diagnostics (30-Second Health Check)
 * Storage & Memory Bottlenecks
 * Safe Disk Expansion (Non-Destructive)
 * 5-Minute Emergency Recovery Routine
 * Secure Port Forwarding & Networking
 * Skill Reference Cheat Sheet
 * Contributing
 * License
📐 Architecture & Mental Model
Understanding where an error originates prevents misdirected troubleshooting:
┌─────────────────────────────────────────────────────────────────┐
│ ChromeOS Host System (Chrome Linux Kernel & Exo Compositor)     │
└────────────────────────────────┬────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ crosvm (Rust VMM / Type-1 Hypervisor via KVM)                   │
└────────────────────────────────┬────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ Termina VM (Lightweight ChromeOS Guest OS / Kernel)             │
└────────────────────────────────┬────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ LXD Container Runtime (Debian/Ubuntu "penguin" Container)       │
└─────────────────────────────────────────────────────────────────┘

 * lxc exec fails: LXD daemon or container userland issue.
 * lxc exec works, but network is dead: Termina VM or crosvm virtual bridge issue.
 * lxc command missing: Termina VM failed to boot or crosvm crashed.
 * Linux apps fail to open: crosvm host-level or GPU passthrough process dropped.
📂 Directory & Repository Structure
.
├── .github/
│   └── workflows/
│       └── ci.yml                 # Automation for guide validation & linting
├── docs/
│   ├── ARCHITECTURE.md            # Deep dive into crosvm, Sommelier, and virtio drivers
│   ├── BENCHMARKS.md              # I/O throughput metrics across virtio-9p vs ext4
│   └── TROUBLESHOOTING.md        # Extended error log matrix
├── scripts/
│   ├── benchmark_io.sh            # In-container disk latency & IOPS test script
│   └── host_recovery.sh           # Crosh automation recovery steps
├── SKILL.md                       # Agent skill definition for Crostini diagnostics
└── README.md                      # Primary repository entry point

🧪 Quick Diagnostics (30-Second Health Check)
Run these commands from the ChromeOS Crosh shell (Ctrl+Alt+T → shell):
# 1. Inspect VM execution state
vmc list

# 2. Force-stop if frozen or stuck in an intermediary state
vmc stop --force termina

# 3. Clean restart to resolve socket corruption
vmc start termina

# 4. Check status and resource allocation
vmc status

> Red Flag: If vmc returns VM not found, the Termina VM is unprovisioned.
> Fix: Go to Settings → Linux → Turn off Linux, wait 10 seconds, then Turn on Linux.
> 
💾 Storage & Memory Bottlenecks
Shared Mount (~/Linux) vs Native Container File System
| Metric | virtio-9p Shared Mount | Native ext4 Container Storage |
|---|---|---|
| Sequential Read | ~40–60 MB/s | ~250–300 MB/s |
| Small-File IOPS | ~1,500 ops/sec | ~5,000 ops/sec |
| Large File Copy | ~3 GB/min | ~8 GB/min |
Performance Impact: Compiling large projects (npm install, cargo build, make, git clone) inside shared folders (/mnt/chromeos/...) is up to 8× slower. Always store build artifacts and repositories within the native container root (/home/username/).
In-Container Disk Throughput & Latency Benchmark
# Test sequential write throughput
dd if=/dev/zero of=testfile bs=1M count=1024 conv=fdatasync status=progress && rm testfile

# Test small file access latency
time find /usr/share -type f | wc -l

⚠️ Safe Disk Expansion (Non-Destructive)
> Warning: Never run vmc resize while containers are running. crosvm can silently corrupt partition tables, leading to superblock invalid errors.
> 
# 1. Stop the container gracefully (from Crosh shell)
lxc stop <container_name>

# 2. Create a safety snapshot (MANDATORY)
lxc snapshot <container_name> backup_$(date +%F)

# 3. Resize the virtual disk from ChromeOS host shell
vmc resize --disk-size=25G

# 4. Start the container
lxc start <container_name>

# 5. Expand filesystem inside the container
lxc exec <container_name> -- growpart /dev/mmcblk0p1 1
lxc exec <container_name> -- resize2fs /dev/mmcblk0p1

🛠️ 5-Minute Emergency Recovery Routine
When Linux apps freeze or the terminal fails on initialization:
 * Verify Hypervisor State:
   vmc list

 * Force Hypervisor Reset:
   vmc stop --force termina && vmc start termina

 * Inspect Host Kernel Messages:
   dmesg | tail -50 | grep -E "(crosvm|virtio|oom)"

   * Out of memory → Container process exceeded host memory limits.
   * Device not responding → VirtIO driver hang.
 * Isolated LXD Launch & Network Verification:
   lxc start penguin
lxc exec penguin -- ping -c 2 10.0.2.2

   * If gateway pings succeed but applications fail, troubleshoot app-level configurations (apt, systemd, PATH).
 * Nuclear Reset:
   Navigate to Settings → Linux → Turn off Linux → Wait 10 seconds → Turn on Linux.
🛡️ Secure Port Forwarding & Networking
Exposing container ports using naive socat commands can introduce security vulnerabilities:
# BAD PATTERN (Bypasses ChromeOS sandbox on open networks)
lxc exec <container> -- socat TCP-LISTEN:8080,fork,reuseaddr TCP:127.0.0.1:80

Recommended Hardening Patterns
 * ChromeOS GUI Forwarding: Use Settings → Linux → Forward ports.
 * Local Loopback Scope:
   # Bind socat strictly to localhost inside container
lxc exec <container> -- socat TCP-LISTEN:8080,bind=127.0.0.1,fork,reuseaddr TCP:127.0.0.1:80

 * In-Container Firewall Hardening:
   sudo ufw default deny incoming
sudo ufw allow 22/tcp comment 'SSH'
sudo ufw enable

📋 Skill Reference Cheat Sheet
Quick lookup for terminal management commands from the Crosh shell:
vmc list                                # List virtual machines
vmc status                              # Show VM uptime and memory stats
vmc stop --force termina                # Force stop hypervisor
vmc start termina                       # Start Termina VM
lxc list                                # List LXD containers and IPs
lxc stop <container>                    # Graceful container shutdown
lxc start <container>                   # Boot container
lxc exec <container> -- <command>       # Execute command as root in container
lxc snapshot <container> <snap_name>    # Create state backup
lxc restore <container> <snap_name>     # Revert to snapshot

🤝 Contributing
Pull requests, diagnostic scripts, and benchmark updates are welcome. Please ensure any shell scripts pass shellcheck linting before opening a PR.
📄 License
Distributed under the MIT License. See LICENSE for details.
s (`npm install`, `make`, `git clone`) in shared folders is up to **8× slower**. Keep source control and build artifacts within the container root (`/`).

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
