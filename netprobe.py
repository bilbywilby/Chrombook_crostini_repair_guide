#!/usr/bin/env python3
"""NETPROBE - zero-dependency privacy probe with a tiny TUI.

Pure Python stdlib. No jq, no pip, no HTML scraping.
Commands: menu | ip | dns | ads | full | history | about

ip   public IPv4/IPv6 + owner (ipify, ipinfo); flags v4/v6 owner mismatch
dns  DNS leak test via the bash.ws protocol (which resolvers saw your queries)
ads  DNS-level ad/tracker blocking test (resolves known ad hosts)
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import json
import os
import re
import socket
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib import request as rq

VERSION = "1.0"
APP = Path(os.environ.get("NETPROBE_HOME", Path.home() / ".netprobe"))
HIST = APP / "history"
UA = {"User-Agent": "netprobe/" + VERSION}
COLOR = sys.stdout.isatty() and "NO_COLOR" not in os.environ
CODES = {"red": 31, "green": 32, "yellow": 33, "cyan": 36, "grey": 90, "bold": 1}
SPARK = "▁▂▃▄▅▆▇█"

ADS = [
    "doubleclick.net", "googlesyndication.com", "googleadservices.com",
    "adservice.google.com", "google-analytics.com", "amazon-adsystem.com",
    "adnxs.com", "criteo.com", "taboola.com", "outbrain.com",
    "scorecardresearch.com", "hotjar.com", "ads.twitter.com",
    "static.ads-twitter.com", "connect.facebook.net", "ads.yahoo.com",
]
CONTROLS = ["example.com", "wikipedia.org"]
SINK = {"0.0.0.0", "127.0.0.1", "::", "::1"}


# ---------------------------------------------------------------- helpers
def c(name: str, text) -> str:
    return f"\033[{CODES[name]}m{text}\033[0m" if COLOR else str(text)


def bar(pct: float, width: int = 20) -> str:
    n = round(width * max(0.0, min(100.0, pct)) / 100)
    tone = "green" if pct >= 85 else "yellow" if pct >= 60 else "red"
    return c(tone, "█" * n) + c("grey", "░" * (width - n))


def spark(vals) -> str:
    return "".join(SPARK[min(7, max(0, round(v / 100 * 7)))] for v in vals)


def head(title: str) -> None:
    print("\n" + c("bold", f"== {title} ==") + "\n")


def get_text(url: str, timeout: int = 8) -> str:
    with rq.urlopen(rq.Request(url, headers=UA), timeout=timeout) as r:
        return r.read().decode("utf-8", "replace").strip()


def get_json(url: str, timeout: int = 8):
    return json.loads(get_text(url, timeout))


def resolve(host: str) -> list[str]:
    try:
        return sorted({a[4][0] for a in socket.getaddrinfo(host, None)})
    except OSError:
        return []


def resolve_many(hosts: list[str], timeout: float = 8.0) -> dict:
    """host -> list of IPs, [] if NXDOMAIN/failed, None if timed out."""
    ex = cf.ThreadPoolExecutor(max_workers=min(16, max(1, len(hosts))))
    futs = {h: ex.submit(resolve, h) for h in hosts}
    out, deadline = {}, time.time() + timeout
    for h, f in futs.items():
        try:
            out[h] = f.result(timeout=max(0.1, deadline - time.time()))
        except cf.TimeoutError:
            out[h] = None
    ex.shutdown(wait=False, cancel_futures=True)
    return out


# ----------------------------------------------------------------- probes
def probe_ip() -> dict:
    r = {"v4": None, "v6": None, "info4": {}, "info6": {}, "error": None}
    for key, url in (("v4", "https://api.ipify.org?format=json"),
                     ("v6", "https://api6.ipify.org?format=json")):
        try:
            r[key] = get_json(url, 6)["ip"]
        except Exception:
            pass
    if not (r["v4"] or r["v6"]):
        r["error"] = "no public IP reachable (offline?)"
        return r
    for fam in ("4", "6"):
        if r["v" + fam]:
            try:
                r["info" + fam] = get_json(
                    f"https://ipinfo.io/{r['v' + fam]}/json")
            except Exception as e:
                r["error"] = f"ipinfo lookup failed: {e}"
    return r


def probe_dns() -> dict:
    r = {"id": None, "servers": [], "error": None}
    try:
        tid = get_text("https://bash.ws/id")
        if not re.fullmatch(r"[A-Za-z0-9]{4,64}", tid):
            raise ValueError("unexpected test id: %r" % tid[:40])
        r["id"] = tid
        resolve_many([f"{i}.{tid}.bash.ws" for i in range(10)], 10)
        data = get_json(f"https://bash.ws/dnsleak/test/{tid}?json", 10)
        r["servers"] = [
            {"ip": d.get("ip"), "country": d.get("country_name"),
             "asn": d.get("asn")}
            for d in data if d.get("type") == "dns"
        ]
    except Exception as e:
        r["error"] = str(e)
    return r


def probe_ads() -> dict:
    res = resolve_many(ADS + CONTROLS, 10)
    ctrl_ok = all(res[h] for h in CONTROLS)
    rows = []
    for h in ADS:
        ips = res[h]
        if ips is None:
            st = "timeout"
        elif not ips or set(ips) <= SINK:
            st = "blocked"
        else:
            st = "open"
        rows.append({"host": h, "status": st, "ips": ips or []})
    blocked = sum(x["status"] == "blocked" for x in rows)
    open_ = sum(x["status"] == "open" for x in rows)
    pct = round(100 * blocked / (blocked + open_), 1) if blocked + open_ else 0.0
    if not ctrl_ok:
        pct = 0.0  # resolver is down: every "block" is a false positive
    return {"pct": pct, "controls_ok": ctrl_ok, "rows": rows}


# ---------------------------------------------------------------- display
def show_ip(r: dict) -> None:
    head("Public IP")
    if r["error"] and not (r["v4"] or r["v6"]):
        print(c("red", r["error"]))
        return
    for fam, label in (("4", "IPv4"), ("6", "IPv6")):
        ip, info = r["v" + fam], r["info" + fam]
        if not ip:
            print(f"{label}: " + c("grey", "none"))
            continue
        where = ", ".join(filter(None, [info.get("city"), info.get("region"),
                                        info.get("country")]))
        print(f"{label}: {c('cyan', ip)}")
        print(f"      {info.get('org', '?')}  |  {where or '?'}")
    o4, o6 = r["info4"].get("org"), r["info6"].get("org")
    if o4 and o6 and o4 != o6:
        print("\n" + c("yellow", "! v4 and v6 owners differ - possible IPv6 leak "
                                 "around your VPN"))
    if r["error"]:
        print("\n" + c("yellow", r["error"]))


def show_dns(r: dict) -> None:
    head("DNS leak test")
    if r["error"]:
        print(c("red", "failed: " + r["error"]))
        return
    if not r["servers"]:
        print(c("yellow", "no resolvers reported (test id %s)" % r["id"]))
        return
    for s in r["servers"]:
        print(f"  {c('cyan', s['ip'] or '?'):<28} {s['country'] or '?'}  "
              f"{c('grey', s['asn'] or '')}")
    print(c("grey", "\nOn a VPN, these should be your VPN/DoH provider - "
                    "not your ISP."))


def show_ads(r: dict) -> None:
    head("DNS-level ad/tracker blocking")
    if not r["controls_ok"]:
        print(c("red", "control domains failed to resolve - DNS is down, "
                       "score is meaningless"))
    if not r["controls_ok"]:
        return
    for x in r["rows"]:
        tag = {"blocked": c("green", "blocked"), "open": c("red", "open   "),
               "timeout": c("yellow", "timeout")}[x["status"]]
        print(f"  {tag}  {x['host']}")
    print(f"\n  {bar(r['pct'])} {r['pct']}% blocked")
    print(c("grey", "  Tests DNS blocking only. Browser extensions and "
                    "cosmetic filters can't be tested from a CLI."))


def save(rep: dict) -> Path:
    HIST.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc)
    rep["ts"] = now.isoformat(timespec="seconds")
    p = HIST / (now.strftime("%Y%m%dT%H%M%SZ") + ".json")
    for path in (p, APP / "latest.json"):
        path.write_text(json.dumps(rep, indent=2), encoding="utf-8")
    return p


def show_history() -> None:
    head("History")
    files = sorted(HIST.glob("*.json"))[-15:] if HIST.exists() else []
    if not files:
        print(c("grey", "no runs yet - try: netprobe.py full"))
        return
    pcts = []
    for f in files:
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        ads = (d.get("ads") or {}).get("pct")
        pcts.append(ads if ads is not None else 0)
        n = len((d.get("dns") or {}).get("servers", []))
        ip = (d.get("ip") or {}).get("v4") or (d.get("ip") or {}).get("v6")
        print(f"  {d.get('ts', f.stem)}  ads {str(ads):>5}%  dns {n}  {ip or '-'}")
    print("\n  ads trend: " + c("cyan", spark(pcts)))


# --------------------------------------------------------------- commands
def run(which: list[str], do_save: bool = False) -> None:
    rep = {}
    for name, fn, view in (("ip", probe_ip, show_ip), ("dns", probe_dns, show_dns),
                           ("ads", probe_ads, show_ads)):
        if name in which:
            print(c("grey", f"probing {name}..."), flush=True)
            rep[name] = fn()
            view(rep[name])
    if do_save:
        print("\n" + c("grey", "saved " + str(save(rep))))


def about() -> None:
    head(f"NETPROBE v{VERSION}")
    print(f"data dir: {APP}\nstdlib only; endpoints: ipify.org, ipinfo.io, bash.ws")


def menu() -> None:
    items = [("1", "My IP", lambda: run(["ip"])),
             ("2", "DNS leak test", lambda: run(["dns"])),
             ("3", "Ad-block (DNS) test", lambda: run(["ads"])),
             ("4", "Full run + save", lambda: run(["ip", "dns", "ads"], True)),
             ("5", "History", show_history),
             ("6", "About", about)]
    while True:
        head("NETPROBE")
        for k, label, _ in items:
            print(f"  {c('cyan', k)}) {label}")
        print(f"  {c('cyan', 'q')}) Quit")
        try:
            ch = input("\n> ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            return
        if ch in ("q", "quit", "exit"):
            return
        for k, _, fn in items:
            if ch == k:
                fn()
                break
        else:
            print(c("yellow", "?"))


def main() -> int:
    ap = argparse.ArgumentParser(prog="netprobe", description=__doc__.splitlines()[0])
    ap.add_argument("cmd", nargs="?", default="menu",
                    choices=["menu", "ip", "dns", "ads", "full", "history", "about"])
    ap.add_argument("--no-color", action="store_true")
    a = ap.parse_args()
    global COLOR
    if a.no_color:
        COLOR = False
    try:
        if a.cmd == "menu":
            menu()
        elif a.cmd == "full":
            run(["ip", "dns", "ads"], True)
        elif a.cmd == "history":
            show_history()
        elif a.cmd == "about":
            about()
        else:
            run([a.cmd])
    except KeyboardInterrupt:
        print()
        return 130
    return 0


if __name__ == "__main__":
    sys.exit(main())

