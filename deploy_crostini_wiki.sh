#!/usr/bin/env bash
set -euo pipefail

REPO_URL="https://github.com/bilbywilby/Chrombook_crostini_repair_guide.wiki.git"
WIKI_DIR="$HOME/Linux/crostini_wiki"

mkdir -p "$HOME/Linux"

if [ -d "$WIKI_DIR" ]; then
  rm -rf "$WIKI_DIR"
fi

git clone "$REPO_URL" "$WIKI_DIR"
cd "$WIKI_DIR"

cat > Home.md <<'EOF_HOME'
# Chromebook Crostini Repair Guide

Welcome to the **Chromebook Crostini Repair Guide** (
