#!/usr/bin/env bash
# Install agentic-kb git hooks into .git/hooks/.
# Idempotent — safe to re-run.
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
SRC="$REPO_ROOT/scripts/hooks"
DST="$REPO_ROOT/.git/hooks"

mkdir -p "$DST"
for hook in pre-push; do
  cp "$SRC/$hook" "$DST/$hook"
  chmod +x "$DST/$hook"
  echo "✓ installed $hook -> $DST/$hook"
done

echo
echo "Hooks installed. To bypass in an emergency: git push --no-verify"
