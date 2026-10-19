#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd -P)"
cd "$ROOT"
command -v claude >/dev/null || {
  echo "Claude CLI is required and must already be authenticated." >&2
  exit 1
}
exec ./launch.sh
