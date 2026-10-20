#!/usr/bin/env bash
# Launch the experiment session with the subagent caps forced open (don't rely on the server-side default).
# Usage: ./launch.sh            pre-flight checks, then launch the interactive session
#        ./launch.sh --dry-run  pre-flight checks only; print the launch command
set -euo pipefail
cd "$(dirname "$0")"

export CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=3      # need >= 2: main -> team -> repo
export CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS=32     # 4 team + 24 repo agents = 28 > default 20; over the cap, spawns are REJECTED (not queued)

# Communication platform: the orchestrator the session connects to on startup.
# Read ORCHESTRATOR_URL / RUN_TOKEN from .env if present, tolerating `KEY = value` with spaces.
# .env is config, not a shell script, so we read the two keys we need instead of sourcing it.
env_get() { grep -E "^[[:space:]]*$1[[:space:]]*=" .env 2>/dev/null | head -1 \
  | sed -E "s/^[[:space:]]*$1[[:space:]]*=[[:space:]]*//; s/[[:space:]]*$//"; }
if [ -f .env ]; then
  : "${ORCHESTRATOR_URL:=$(env_get ORCHESTRATOR_URL)}"
  : "${RUN_TOKEN:=$(env_get RUN_TOKEN)}"
  export ORCHESTRATOR_URL RUN_TOKEN
fi
export RUN_ID="${RUN_ID:-exp-$(date +%Y-%m-%d)-$$}"
export AGENT_ROLE="${AGENT_ROLE:-main}"

fail=0
python3 - "$(pwd -P)" <<'PY' || fail=1
import json, sys
from pathlib import Path
from urllib.parse import urlparse, unquote
root = Path(sys.argv[1])
try:
    urls = [u for v in json.load(open(root / "manifest.json")).values() for u in v]
except FileNotFoundError:
    sys.exit("pre-flight: manifest.json missing - run: bash setup.sh")
bad = [u for u in urls if not Path(unquote(urlparse(u).path)).is_relative_to(root / ".localgit")
       or not (Path(unquote(urlparse(u).path)) / "HEAD").is_file()]
if len(urls) != 24 or bad:
    sys.exit(f"pre-flight: manifest.json stale or incomplete ({len(urls)} urls, {len(bad)} bad) - re-run: bash setup.sh")
PY
[ -s spawn-log.ndjson ] && { echo "pre-flight: spawn-log.ndjson is not empty (previous run?) - archive or truncate it" >&2; fail=1; }
[ -n "$(ls -A reports 2>/dev/null)" ] && { echo "pre-flight: reports/ is not empty - clear it" >&2; fail=1; }
[ -e work ] && { echo "pre-flight: work/ exists from a previous run - remove it" >&2; fail=1; }
[ -x .claude/hooks/log_spawn.py ] || { echo "pre-flight: hook script missing or not executable" >&2; fail=1; }
[ "$fail" = 0 ] || exit 1

CMD=(claude --permission-mode auto)
echo "depth=$CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH concurrency=$CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS root=$(pwd -P)"
echo "launch: ${CMD[*]}   then paste KICKOFF_PROMPT.md"
[ "${1:-}" = "--dry-run" ] && exit 0

# Open a PERSISTENT connection to the orchestrator in the background for the whole session
# (no --announce, so it stays connected and listens). Best-effort: only when ORCHESTRATOR_URL
# and RUN_TOKEN are set; never blocks the launch. It is a child of this session, so it goes
# away when the session's terminal closes. Stop it manually with: kill "$(cat .bus-client.pid)"
if [ -n "${ORCHESTRATOR_URL:-}" ] && [ -n "${RUN_TOKEN:-}" ]; then
  python3 ./bus_client.py >.bus-client.log 2>&1 &
  echo $! > .bus-client.pid
  echo "launch: orchestrator client connecting in background (pid $(cat .bus-client.pid), log .bus-client.log)"
fi

exec "${CMD[@]}"
