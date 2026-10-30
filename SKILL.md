---
name: crostini-repair-guide
description: Diagnose and repair ChromeOS Linux (Crostini) problems on Chromebooks. Use when the user reports Linux apps or the Terminal not starting, the container or Termina VM stuck or stopped, "no space left on device", resizing the Linux disk, no network or DNS inside the container, slow file access, ports not reachable from ChromeOS or other devices, USB or GPU questions, lost integration (launcher icons, file sharing, clipboard), or wants to back up, restore or reset Linux.
---

# Crostini Repair Guide

Triage Crostini top-down, fix with the least destructive step first, and never state a command works unless it is on the verified list below.

## Rules for the assistant

1. **Ask first, once:** is the device in developer mode (can they run `shell` in crosh)? ChromeOS version? Which container name (default `penguin`)? Most users are NOT in developer mode; give crosh-only paths unless told otherwise.
2. **Backup before anything destructive.** Order of destructiveness is in section 9. Never suggest `vmc destroy`, "Remove", or powerwash without first confirming a backup exists or the data is disposable.
3. **Use only verified commands** (section 10). If a command from memory is not on that list, say "verify with `vmc help` / `lxc --help`" instead of presenting it as fact.
4. **Do not invent numbers.** No throughput, IOPS or "X% of failures" claims. Give a measurement command instead.
5. **Prefer the Settings UI over CLI** for resize, backup and port forwarding. The UI handles the filesystem layers for you.

## 1. Architecture (what runs where)

```
ChromeOS host
 └─ crosvm (KVM-based VMM, written in Rust)
     └─ Termina VM (minimal Linux; runs LXD)
         └─ LXD container "penguin" (Debian by default; your apps live here)
```

Integration glue lives *inside* the container (package `cros-guest-tools`: garcon for launcher/app integration, sommelier for display). Plenty of "Crostini is broken" cases are this glue breaking after a distro upgrade, not the hypervisor.

## 2. Where each command runs

| Shell | How to get it | What works there |
|---|---|---|
| **crosh** | Ctrl+Alt+T | `vmc ...`, `vsh ...`. No `lxc`, no `iptables`, no `dmesg` |
| **termina** | in crosh: `vmc start termina` then `vsh termina` | `lxc ...`, `dmesg`, `free`, `df`, `ip` (VM-level) |
| **container** | Terminal app, or `vsh termina penguin` from crosh, or `lxc exec penguin -- bash` from termina | normal Linux: apt, systemctl, journalctl, ip, df |
| **host shell** | crosh `shell` | **developer mode only.** Do not assume it exists |

## 3. Triage by symptom

| Symptom | First check | Likely layer |
|---|---|---|
| Terminal app won't open / spins forever | `vmc list`, then section 4 | VM or container not running |
| "No space left on device" | `df -h /` in container; section 5 | disk allocation |
| Container stuck "Stopped" / fails to start | `lxc list`, `lxc info penguin --show-log` (termina) | container / LXD |
| Container runs but no internet | section 6 | network / DNS / VPN |
| Apps missing from launcher, no file sharing, no clipboard | section 7 | cros-guest-tools / garcon |
| Everything slow, builds crawl | section 8 | storage location or RAM |
| Server in container unreachable from ChromeOS or phone | section 9a | port forwarding |
| Broke after a Debian release upgrade | section 7 first | cros-guest-tools |

## 4. VM health check (crosh, 1 minute)

```
vmc list                  # is termina present? size shown
vmc start termina         # starts it (drops you in a termina shell; type exit to leave)
vsh termina               # enter termina
lxc list                  # container state: RUNNING / STOPPED, IPv4 present?
```

If the container is stopped: `lxc start penguin`, then `lxc info penguin --show-log` and read the last lines for the real error.

If the VM is wedged: `vmc stop termina` then `vmc start termina`. (There is no `--force` flag in the verified set. If `vmc stop` hangs, restart ChromeOS.)

Also try the shelf: right-click the Terminal icon → **Shut down Linux**, then reopen Terminal. This is the non-destructive restart.

## 5. Disk full / resize (do this in Settings)

1. Free space first inside the container: `df -h /`, `du -xh --max-depth=1 ~ | sort -h | tail`, `sudo apt clean`, `docker system df` if Docker is installed.
2. **Settings → Developers → Linux development environment → Disk size → Change.** Shut down Linux first if prompted. The slider resizes the VM disk and filesystem for you.
3. Do **not** run `growpart`, `resize2fs` or `xfs_growfs` inside the container. The container's root is not a partition you manage; Settings does the resize across the layers.
4. Back up before big changes: **Settings → Linux development environment → Backup & restore → Back up.**
5. To shrink below current use, or after corruption: back up, Remove Linux, re-enable with a smaller size, restore.

Check termina-level space if the container looks fine but LXD errors: `vsh termina` then `df -h /mnt/stateful`.

## 6. Networking

Inside the container:

```
ip a                          # eth0 present with an address?
ip route                      # note the default gateway; do not assume an address
ping -c 2 <gateway from ip route>
ping -c 2 1.1.1.1             # internet by IP
getent hosts example.com      # DNS
resolvectl status || cat /etc/resolv.conf
```

Interpretation: IP ping ok but DNS fails → DNS (check VPN/Android VPN, custom DNS in ChromeOS network settings). Gateway ping fails → restart Linux (section 4). Everything fails only on one Wi-Fi → network policy, test on a hotspot.

Crostini does not use the `10.0.2.x` addresses seen in QEMU examples. Read the gateway from `ip route`.

## 7. Lost integration (no icons, no file sharing, no clipboard)

In the container:

```
sudo apt update && sudo apt install --reinstall cros-guest-tools
systemctl --user status cros-garcon     # service names vary a bit by release
sudo systemctl status cros-sftp
```

Then shut down Linux from the shelf and reopen Terminal. If this fails after a distro upgrade, check that `/etc/apt/sources.list.d/cros.list` still exists and that the apt repo for `cros-guest-tools` resolves.

File sharing: in the Files app, right-click a folder → **Share with Linux**. Shared folders appear under `/mnt/chromeos/` in the container. "Linux files" in the Files app is your container home viewed from ChromeOS.

## 8. Performance

Measure, do not guess:

```
free -m                                   # RAM pressure in the container
df -h / /mnt/chromeos 2>/dev/null         # where data actually lives
dd if=/dev/zero of=~/ddtest bs=1M count=512 conv=fdatasync status=progress; rm ~/ddtest
dd if=/dev/zero of=/mnt/chromeos/MyFiles/ddtest bs=1M count=512 conv=fdatasync status=progress; rm /mnt/chromeos/MyFiles/ddtest
```

Compare the two `dd` results on the user's own device. Rule of thumb: keep repos, `node_modules`, build output and databases in the container home, not under `/mnt/chromeos`, because shared ChromeOS folders cross the VM boundary and are slower for many small files. For memory kills, run `dmesg | tail -50` in **termina** (`vsh termina`) and look for `Out of memory` / `Killed process`.

## 9. Ports, USB, GPU

**a) Reaching a server in the container**
- A server listening in the container is usually reachable from ChromeOS at `http://localhost:<port>` (auto-forward for listening ports) or `http://penguin.linux.test:<port>`.
- To reach it from **other devices on the LAN**: Settings → Developers → Linux development environment → **Port forwarding** → Add. This opens the port on the ChromeOS host's network interface, so anyone on that network can connect. Use it only on trusted networks, turn it off when done, and bind the dev server to a specific interface if the app allows it.
- `socat` is rarely needed. Do not tell users that binding `0.0.0.0` inside the container exposes them to the Wi-Fi by itself; the Port forwarding setting is what opens the host side. Do not tell users to run `iptables` on the host; it is not available in normal mode.

**b) USB:** Settings → Developers → Linux development environment → **Manage USB devices** lets you attach supported USB devices to Linux. Device support varies, and some classes (e.g. certain storage, audio, hubs) may not attach. Do not claim "no USB passthrough".

**c) GPU:** hardware acceleration availability depends on device and ChromeOS version. Check with `glxinfo -B` (package `mesa-utils`). Do not give `lxc config device add ... gpu` as a fix; it is not a supported Crostini setup.

## 10. Verified command set (use these; flag anything else as "verify")

crosh: `vmc list`, `vmc start termina`, `vmc stop termina`, `vmc destroy termina` (**destroys the VM and all containers**), `vmc container <vm> <container>`, `vsh termina`, `vsh termina penguin`

termina: `lxc list`, `lxc start|stop|restart <name>`, `lxc info <name> [--show-log]`, `lxc exec <name> -- <cmd>`, `lxc snapshot <name> <snap>`, `lxc restore <name> <snap>`, `lxc delete <name>` (destroys the container), `dmesg`, `free -m`, `df -h`

**Commands that do not exist or do not apply (earlier drafts invented them):** `vmc status`, `vmc stop --force`, `vmc shell`, `vmc set --cpus`, `vmc resize` as the recommended path, `chromeos-firmware-management`, `lxc config device add ... gpu` as a fix, `iptables`/`ufw` on the ChromeOS host, `ps aux | grep crosvm` from crosh.

## 11. Escalation ladder (least → most destructive)

1. Reopen Terminal.
2. Shelf icon → **Shut down Linux**, reopen.
3. crosh: `vmc stop termina`, `vmc start termina`.
4. Reboot ChromeOS.
5. `lxc snapshot` the container, then retry the fix.
6. **Backup & restore → Back up** (Settings), copy the backup off-device.
7. **Settings → Developers → Linux development environment → Remove** (deletes all Linux data).
8. `vmc destroy termina` (deletes the VM and every container).
9. Powerwash (wipes the device).

Never go past step 6 without a verified, off-device backup.

## 12. Output style

Imperative and terse. Give the command, what output to expect, and what to do for each outcome. State which shell each command runs in. When unsure of a ChromeOS-version-specific detail, say so and give the way to verify.
