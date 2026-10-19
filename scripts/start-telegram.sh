#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd -P)"
cd "$ROOT"
VENV="$ROOT/.telegram-venv"
PIDFILE="$ROOT/.runtime/telegram.pid"
LOGFILE="$ROOT/.runtime/telegram.log"

[[ -x "$VENV/bin/python" ]] || { echo "Run ./bootstrap.sh first." >&2; exit 1; }
"$VENV/bin/python" telegram_comunication.py --validate-config
mkdir -p "$ROOT/.runtime"
if [[ -f "$PIDFILE" ]] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
  echo "Telegram bridge is already running (PID $(cat "$PIDFILE"))."
  exit 0
fi
rm -f "$PIDFILE"
nohup "$VENV/bin/python" "$ROOT/telegram_comunication.py" >>"$LOGFILE" 2>&1 &
pid=$!
echo "$pid" >"$PIDFILE"
sleep 1
if ! kill -0 "$pid" 2>/dev/null; then
  echo "Telegram bridge exited; see $LOGFILE" >&2
  rm -f "$PIDFILE"
  exit 1
fi
echo "Telegram bridge started (PID $pid). Log: $LOGFILE"
