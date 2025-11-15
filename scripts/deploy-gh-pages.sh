#!/usr/bin/env bash

set -euo pipefail

BRANCH=${BRANCH:-gh-pages}
REMOTE=${REMOTE:-origin}
SOURCE_DIR=${SOURCE_DIR:-docs}
SITE_DIR=${SITE_DIR:-build/html}
WORKTREE_DIR=${WORKTREE_DIR:-build/.gh-pages-worktree}
PYTHON_BIN=${PYTHON:-python3}
COMMIT_MSG=${1:-"Deploy site"}

if ! command -v git >/dev/null 2>&1; then
  echo "Error: git is required but was not found in PATH." >&2
  exit 1
fi

if ! command -v rsync >/dev/null 2>&1; then
  echo "Error: rsync is required but was not found in PATH." >&2
  exit 1
fi

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "Error: '$PYTHON_BIN' was not found in PATH. Set PYTHON to the desired interpreter." >&2
  exit 1
fi

ROOT_DIR=$(git rev-parse --show-toplevel 2>/dev/null || true)
if [[ -z "$ROOT_DIR" ]]; then
  echo "Error: This script must be run inside a git repository." >&2
  exit 1
fi

cd "$ROOT_DIR"

if ! git remote get-url "$REMOTE" >/dev/null 2>&1; then
  echo "Error: Remote '$REMOTE' is not configured." >&2
  exit 1
fi

if [[ ! -d "$SOURCE_DIR" ]]; then
  echo "Error: Source directory '$SOURCE_DIR' does not exist." >&2
  exit 1
fi

# Build the static site before touching the gh-pages worktree.
"$PYTHON_BIN" -m md2html --src "$SOURCE_DIR" --dst "$SITE_DIR"

if [[ ! -d "$SITE_DIR" ]]; then
  echo "Error: Site output directory '$SITE_DIR' was not created." >&2
  exit 1
fi

# Ensure a clean worktree location before re-adding it.
git worktree remove --force "$WORKTREE_DIR" >/dev/null 2>&1 || true
rm -rf "$WORKTREE_DIR"
git worktree prune >/dev/null 2>&1 || true

cleanup() {
  git worktree remove --force "$WORKTREE_DIR" >/dev/null 2>&1 || true
  rm -rf "$WORKTREE_DIR"
}
trap cleanup EXIT

NEW_BRANCH=0
if git show-ref --verify --quiet "refs/heads/$BRANCH"; then
  git worktree add --force "$WORKTREE_DIR" "$BRANCH"
elif git ls-remote --exit-code "$REMOTE" "$BRANCH" >/dev/null 2>&1; then
  git fetch "$REMOTE" "$BRANCH:$BRANCH"
  git worktree add --force "$WORKTREE_DIR" "$BRANCH"
else
  NEW_BRANCH=1
  git worktree add --force "$WORKTREE_DIR" --detach
  git -C "$WORKTREE_DIR" switch --orphan "$BRANCH"
fi

# Sync the freshly built site into the gh-pages worktree.
rsync -av --delete "$SITE_DIR"/ "$WORKTREE_DIR"/

touch "$WORKTREE_DIR/.nojekyll"

if [[ -f "$ROOT_DIR/CNAME" ]]; then
  cp "$ROOT_DIR/CNAME" "$WORKTREE_DIR/CNAME"
fi

if [[ -z $(git -C "$WORKTREE_DIR" status --porcelain) ]]; then
  echo "No changes to deploy." >&2
  exit 0
fi

git -C "$WORKTREE_DIR" add --all
git -C "$WORKTREE_DIR" commit -m "$COMMIT_MSG"

if [[ $NEW_BRANCH -eq 1 ]]; then
  git -C "$WORKTREE_DIR" push --set-upstream "$REMOTE" "$BRANCH"
else
  git -C "$WORKTREE_DIR" push "$REMOTE" "$BRANCH"
fi

echo "Deployment complete."
