#!/usr/bin/env bash
# commit_push_pull.sh
# Stage all changes, commit, push to main, then pull/reconcile.
#
# Overridable:
#   REPO_DIR=~/path BRANCH=main COMMIT_MSG="msg" ./commit_push_pull.sh
set -euo pipefail

REPO_DIR="${REPO_DIR:-$HOME/Chrombook_crostini_repair_guide}"
BRANCH="${BRANCH:-main}"
REMOTE="${REMOTE:-origin}"
COMMIT_MSG="${COMMIT_MSG:-Sync Crostini guide docs and wiki sources}"
LARGE_FILE_MB="${LARGE_FILE_MB:-25}"

die()  { printf '\033[31mERROR:\033[0m %s\n' "$*" >&2; exit 1; }
info() { printf '\033[36m==>\033[0m %s\n' "$*"; }
warn() { printf '\033[33mWARN:\033[0m %s\n' "$*" >&2; }

command -v git >/dev/null 2>&1 || die "git not found"
[ -d "$REPO_DIR" ] || die "repo directory not found: $REPO_DIR"
cd "$REPO_DIR"
git rev-parse --is-inside-work-tree >/dev/null 2>&1 || die "not a git repository: $REPO_DIR"

# ---- identity (needed or the commit fails) --------------------------------
git config user.name  >/dev/null 2>&1 || git config user.name  "$(whoami)"
git config user.email >/dev/null 2>&1 || git config user.email "$(whoami)@localhost"

# ---- branch sanity -------------------------------------------------------
current="$(git symbolic-ref --short -q HEAD || true)"
[ -n "$current" ] || die "detached HEAD; run: git checkout $BRANCH"
if [ "$current" != "$BRANCH" ]; then
  die "on branch '$current' but BRANCH='$BRANCH'. Re-run as: BRANCH=$current $0"
fi

info "Repository : $REPO_DIR"
info "Branch     : $current -> $REMOTE/$BRANCH"

# ---- pre-flight: junk and oversized files --------------------------------
junk_found=()
for candidate in FETCH_HEAD manifest_report.json; do
  if [ -e "$candidate" ] && [ -z "$(git ls-files -- "$candidate")" ]; then
    junk_found+=("$candidate")
  fi
done
if [ "${#junk_found[@]}" -gt 0 ]; then
  warn "these look like generated artefacts and will be committed:"
  printf '        %s\n' "${junk_found[@]}" >&2
  warn "add them to .gitignore if that is not intended."
fi

big=()
while IFS= read -r f; do
  [ -n "$f" ] || continue
  [ -f "$f" ] || continue
  size="$(wc -c <"$f" 2>/dev/null || echo 0)"
  if [ "$size" -gt $((LARGE_FILE_MB * 1024 * 1024)) ]; then
    big+=("$(du -h "$f" | cut -f1)	$f")
  fi
done < <(git ls-files --others --exclude-standard; git diff --name-only)

if [ "${#big[@]}" -gt 0 ]; then
  warn "files larger than ${LARGE_FILE_MB}MB:"
  printf '        %s\n' "${big[@]}" >&2
  warn "GitHub hard-rejects individual files over 100MB."
fi

# ---- stage and commit ----------------------------------------------------
info "Staging all changes"
git add -A

if git diff --cached --quiet; then
  info "Nothing to commit; working tree already matches HEAD."
else
  staged_count="$(git diff --cached --name-only | wc -l | tr -d ' ')"
  info "Committing $staged_count file(s)"
  git commit -m "$COMMIT_MSG"
fi

# ---- push (with one rebase retry) ----------------------------------------
info "Pushing to $REMOTE/$BRANCH"
if ! git push "$REMOTE" "$BRANCH"; then
  warn "push rejected; fetching and rebasing onto $REMOTE/$BRANCH"
  git fetch "$REMOTE" "$BRANCH"
  if ! git rebase "$REMOTE/$BRANCH"; then
    git rebase --abort || true
    die "rebase conflict. Resolve manually, then re-run."
  fi
  git push "$REMOTE" "$BRANCH"
fi
info "Push complete"

# ---- pull / reconcile ----------------------------------------------------
info "Reconciling with $REMOTE/$BRANCH"
git fetch "$REMOTE" "$BRANCH"

if ! git rev-parse --verify --quiet "$REMOTE/$BRANCH" >/dev/null; then
  warn "no remote-tracking ref for $REMOTE/$BRANCH; skipping pull."
elif git merge-base --is-ancestor HEAD "$REMOTE/$BRANCH"; then
  git merge --ff-only "$REMOTE/$BRANCH"
  info "Fast-forwarded to $REMOTE/$BRANCH"
elif git merge-base --is-ancestor "$REMOTE/$BRANCH" HEAD; then
  info "Local is ahead of remote; nothing to pull."
else
  warn "branches diverged; rebasing local commits onto remote"
  if ! git rebase "$REMOTE/$BRANCH"; then
    git rebase --abort || true
    die "rebase conflict during pull. Resolve manually."
  fi
  info "Rebased onto $REMOTE/$BRANCH"
fi

# ---- summary -------------------------------------------------------------
printf '\n'
info "Done."
git --no-pager log --oneline --decorate -n 5
printf '\n'
git status --short --branch
