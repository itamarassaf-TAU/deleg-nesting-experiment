#!/usr/bin/env python3
"""PreToolUse hook: append one NDJSON line per Task/Agent/Bash call to <repo root>/spawn-log.ndjson. Never blocks."""
import datetime, fcntl, json, sys
from pathlib import Path

LOG = Path(__file__).resolve().parents[2] / "spawn-log.ndjson"  # .claude/hooks/ -> repo root

try:
    ev = json.load(sys.stdin)
    rec = {
        "ts": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="milliseconds"),
        "tool": ev.get("tool_name"),
        "input": json.dumps(ev.get("tool_input", {}), ensure_ascii=False)[:300],
        # extra context for rebuilding the tree; absent fields are omitted
        **{k: ev[k] for k in ("session_id", "agent_id", "agent_type", "tool_use_id", "cwd") if ev.get(k)},
    }
    with open(LOG, "a") as f:
        fcntl.flock(f, fcntl.LOCK_EX)  # concurrent subagents append safely
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
except Exception as e:
    print(f"log_spawn hook error: {e}", file=sys.stderr)
sys.exit(0)
