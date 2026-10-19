#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd -P)"
PIDFILE="$ROOT/.runtime/telegram.pid"
if [[ ! -f "$PIDFILE" ]]; then
  echo "Telegram bridge is not running."
  exit 0
fi
pid="$(cat "$PIDFILE")"
if kill -0 "$pid" 2>/dev/null; then
  kill "$pid"
  for _ in {1..20}; do
    kill -0 "$pid" 2>/dev/null || break
    sleep 0.25
  done
fi
rm -f "$PIDFILE"
echo "Telegram bridge stopped."
