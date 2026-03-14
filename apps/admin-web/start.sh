#!/usr/bin/env bash
set -euo pipefail

npm run dev -- --host 0.0.0.0 --port ${FRONTEND_PORT:-3000}
