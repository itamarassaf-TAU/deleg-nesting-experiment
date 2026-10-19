#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd -P)"
PIDFILE="$ROOT/.runtime/telegram.pid"
if [[ -f "$PIDFILE" ]] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
  echo "Telegram bridge: running (PID $(cat "$PIDFILE"))"
else
  echo "Telegram bridge: stopped"
  [[ -f "$PIDFILE" ]] && rm -f "$PIDFILE"
fi
