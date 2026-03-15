#!/bin/sh
set -eu

LOCK_HASH_FILE="node_modules/.package-lock.sha256"
CURRENT_LOCK_HASH="$(sha256sum package-lock.json | awk '{print $1}')"
STORED_LOCK_HASH="$(cat "$LOCK_HASH_FILE" 2>/dev/null || true)"

if [ ! -d node_modules ] || [ "$CURRENT_LOCK_HASH" != "$STORED_LOCK_HASH" ]; then
  npm ci
  mkdir -p node_modules
  printf "%s" "$CURRENT_LOCK_HASH" > "$LOCK_HASH_FILE"
fi

npm run dev -- --host ${FRONTEND_HOST:-0.0.0.0} --port ${FRONTEND_PORT:-3000}
