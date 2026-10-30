# Crostini Repair & Diagnosis — Skill Architecture

## 1. Skill Metadata

* **Skill Identifier:** `crostini-repair-guide`
* **Title:** Crostini Diagnosis & Repair — Power User Field Manual
* **Core Philosophy:** Top-down host-first troubleshooting ($\text{Host / crosvm} \longrightarrow \text{Termina VM} \longrightarrow \text{LXD Container}$).
* **Primary Objective:** Diagnose and resolve ChromeOS Linux environment failures at the hypervisor and virtual machine layers before attempting container-level fixes.

---

## 2. Trigger Matrix & Intent Mapping

| User Intent / Query Phrase | Mapped Action / Workflow | Target Layer |
| :--- | :--- | :--- |
| *"My Crostini apps crash instantly or freeze"* | Hypervisor status check & `dmesg` OOM inspection | Host (`crosvm`) |
| *"How do I safely increase Linux disk without bricking?"* | Non-destructive snapshot $\rightarrow$ `vmc resize` $\rightarrow$ `growpart` | VM & Container |
| *"Termina VM won't start / socket closed"* | Force-kill Termina VM and clean restart | VM (`Termina`) |
| *"Port forwarding inside Crostini is slow or insecure"* | Sandbox-aware loopback binding + `iptables` whitelist | Network / Host |
| *"Linux environment completely disappeared"* | Unprovisioned check & re-provisioning guidance | Host (`Crosh`) |

---

## 3. Layered Stack Architecture

```text
┌─────────────────────────────────────────────────────────────┐
│ 1. ChromeOS Host System                                    │
│    - Kernel & Exo Compositor                                │
│    - Crosh Shell (`Ctrl+Alt+T` -> `shell`)                 │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. crosvm Hypervisor Layer (Rust-based VMM)                 │
│    - Silent memory limits & VirtIO device mapping           │
│    - Process inspect: `ps aux | grep crosvm`               │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. Termina VM Layer (Minimal ChromeOS Linux)                │
│    - Managed via `vmc` (`start`, `stop`, `resize`)         │
│    - Internal DNS forwarder at `10.0.2.3`                  │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. LXD Container Layer ("penguin" / custom containers)      │
│    - Managed via `lxc` (`exec`, `snapshot`, `restore`)     │
│    - Native ext4 file system vs virtio-9p shared mount      │
└─────────────────────────────────────────────────────────────┘
```

---

## 4. Workflows & Execution Pipelines

### Workflow A: 30-Second Hypervisor Health Check
```bash
# Execute within Crosh (Ctrl+Alt+T)
vmc list
vmc stop --force termina
vmc start termina
vmc status
```

### Workflow B: Non-Destructive Storage Expansion
```bash
# 1. Stop container (Host)
lxc stop <container_name>

# 2. Mandatory safety snapshot (Host)
lxc snapshot <container_name> backup_$(date +%F)

# 3. Host disk resize (Host)
vmc resize --disk-size=25G

# 4. Boot container (Host)
lxc start <container_name>

# 5. Expand container partition (Guest)
lxc exec <container_name> -- growpart /dev/mmcblk0p1 1
lxc exec <container_name> -- resize2fs /dev/mmcblk0p1
```

### Workflow C: Secure Port Exposure
```bash
# Bind strictly to loopback inside container
lxc exec <container_name> -- socat TCP-LISTEN:8080,bind=127.0.0.1,fork,reuseaddr TCP:127.0.0.1:80

# Explicitly whitelist on host firewall
sudo iptables -A INPUT -p tcp --dport 8080 -j ACCEPT
```

---

## 5. Performance Baselines (`virtio-9p` vs Native `ext4`)

$$\begin{array}{|l|c|c|}
\hline
\textbf{Metric} & \textbf{virtio-9p Shared Mount (\text{\sim}/Linux)} & \textbf{Native ext4 Container Storage} \\ \hline
\text{Sequential Read} & \sim 40\text{--}60\text{ MB/s} & \sim 250\text{--}300\text{ MB/s} \\ \hline
\text{Small-File IOPS} & \sim 1,500\text{ ops/sec} & \sim 5,000\text{ ops/sec} \\ \hline
\text{Large File Copy} & \sim 3\text{ GB/min} & \sim 8\text{ GB/min} \\ \hline
\end{array}$$

*Rule:* Heavy compilation steps, `node_modules`, and Git repositories must reside on native `ext4` container paths (`/home/user/`) rather than host-shared mounts.