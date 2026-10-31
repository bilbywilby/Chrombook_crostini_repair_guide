#!/usr/bin/env python3
import os, subprocess, sys, re
from pathlib import Path

OWNER_REPO = "bilbywilby/Chrombook_crostini_repair_guide"
REPO_URL = f"https://github.com/{OWNER_REPO}.wiki.git"
WIKI_DIR = Path.home() / "Linux" / "crostini_wiki"
BRANCH = "master"
NAV_BEGIN = "<!-- BEGIN crostini-guide-nav -->"
NAV_END = "<!-- END crostini-guide-nav -->"

NAV_BLOCK = "\n".join([
    NAV_BEGIN, "",
    "## Guide Sections", "",
    "* [[Architecture Overview|Architecture-Overview]]",
    "* [[Command Context & Repair Pipelines|Repair-Pipelines]]",
    "* [[Diagnostic Tools|Diagnostic-Tools]]",
    "* [[Test Suite Reference|Test-Suite-Reference]]",
    "* [[Backup Automation|Backup-Automation]]",
    "* [[Emergency Recovery|Emergency-Recovery]]",
    "", NAV_END,
])

def run(cmd, cwd=None, check=True):
    print("  $ " + " ".join(str(c) for c in cmd))
    result = subprocess.run([str(c) for c in cmd], cwd=cwd, capture_output=True, text=True, check=False)
    if check and result.returncode != 0:
        print(f"STDERR: {result.stderr}")
        result.check_returncode()
    return result

def upsert_block(text, block, begin, end):
    pattern = re.compile(re.escape(begin) + r".*?" + re.escape(end), re.DOTALL)
    if pattern.search(text):
        return pattern.sub(lambda _: block, text)
    lines = text.splitlines(keepends=True)
    insert_at = next((i+1 for i, l in enumerate(lines) if l.lstrip().startswith("#")), 0)
    head = "".join(lines[:insert_at]).rstrip("\n") + "\n\n"
    tail = "".join(lines[insert_at:]).lstrip("\n")
    return head + block + "\n\n" + tail

def find_source_file(filename):
    for path in [Path(filename), Path("wiki") / filename, Path("docs") / filename]:
        if path.is_file():
            return path
    raise FileNotFoundError(f"Could not locate source file: {filename}")

def main():
    WIKI_DIR.parent.mkdir(parents=True, exist_ok=True)
    print("Checking wiki endpoint...")
    probe = run(["git", "ls-remote", REPO_URL], check=False)
    if probe.returncode != 0:
        raise SystemExit(f"ERROR: {REPO_URL} unreachable. Create first wiki page via GitHub UI.")

    print(f"Wiki clone at {WIKI_DIR}")
    if (WIKI_DIR / ".git").is_dir():
        run(["git", "fetch", "origin", BRANCH], cwd=WIKI_DIR)
        run(["git", "reset", "--hard", f"origin/{BRANCH}"], cwd=WIKI_DIR)
    else:
        run(["git", "clone", REPO_URL, str(WIKI_DIR)])

    run(["git", "config", "user.name", "deploy-bot"], cwd=WIKI_DIR, check=False)
    run(["git", "config", "user.email", "deploy@localhost"], cwd=WIKI_DIR, check=False)

    page_names = ["Diagnostic-Tools.md", "Repair-Pipelines.md", "Test-Suite-Reference.md", "Backup-Automation.md", "Emergency-Recovery.md"]
    pages = {name: find_source_file(name).read_text(encoding="utf-8") for name in page_names}

    home = WIKI_DIR / "Home.md"
    if home.is_file():
        orig = home.read_text(encoding="utf-8")
        updated = upsert_block(orig, NAV_BLOCK, NAV_BEGIN, NAV_END)
        if updated != orig:
            home.write_text(updated, encoding="utf-8")
            print("Home.md: nav merged")
        else:
            print("Home.md: nav already present")
    else:
        home.write_text(f"# Chromebook Crostini Repair Guide\n\n{NAV_BLOCK}\n", encoding="utf-8")
        print("Home.md: created")

    for name, content in pages.items():
        path = WIKI_DIR / name
        if not path.exists() or path.read_text(encoding="utf-8") != content:
            path.write_text(content, encoding="utf-8")
            print(f"{name}: written")

    run(["git", "add", "-A"], cwd=WIKI_DIR)
    if run(["git", "diff", "--cached", "--quiet"], cwd=WIKI_DIR, check=False).returncode == 0:
        print("No changes to publish.")
        return
    run(["git", "commit", "-m", "Deploy wiki pages from main repo"], cwd=WIKI_DIR)
    run(["git", "push", "origin", BRANCH], cwd=WIKI_DIR)
    print("✓ Wiki deployed to", WIKI_DIR)

if __name__ == "__main__":
    main()
