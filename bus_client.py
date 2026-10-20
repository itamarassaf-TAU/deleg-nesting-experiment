#!/usr/bin/env python3
"""The communication platform for this experiment.

Replaces the old telegram bot. An agent process connects to the orchestrator on
startup, registers (and so gets an address), and exchanges *structured* messages
with its parent and the orchestrator.

The defining difference from the telegram bot it replaces: this client does NOT
execute what it receives. The old bot ran `claude -p <incoming text>`, which made
anyone who could message it a remote shell. This client transports structured
envelopes and prints received ones as data. What to do with a message is the
agent's decision, made with its own bounded tools — receiving one never runs
anything by itself.

Env (set by launch.sh, or your shell):
    ORCHESTRATOR_URL   wss://<host>   (ws://127.0.0.1:8080 for local)
    RUN_TOKEN          per-run shared secret (must match the server; never commit)
    RUN_ID             identifier for this run
    AGENT_ROLE         main | team-agent | repo-agent     (default: main)
    AGENT_TEAM         team name          (team-agent / repo-agent)
    AGENT_REPO         repo name          (repo-agent)
    AGENT_PARENT       parent address     (e.g. main, or team-agent:payments)

Usage:
    python bus_client.py                 # connect on startup, register, listen
    python bus_client.py --announce      # register, send one 'status: up', exit
"""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys

try:
    import websockets
except ImportError:
    # Fall back to a dedicated venv next to this file, so the SessionStart hook (and
    # launch.sh) can invoke a bare `python3` even when the system interpreter lacks
    # websockets (e.g. a PEP 668 externally-managed Homebrew Python).
    _venv_py = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".bus-venv", "bin", "python")
    if os.path.exists(_venv_py) and os.path.realpath(_venv_py) != os.path.realpath(sys.executable):
        os.execv(_venv_py, [_venv_py, os.path.abspath(__file__), *sys.argv[1:]])
    sys.exit("bus_client: missing dependency 'websockets'. Create the venv once:\n"
             "  uv venv .bus-venv && uv pip install --python .bus-venv/bin/python websockets==12.0")

MAX_PAYLOAD_BYTES = 256 * 1024


def _cfg() -> dict:
    try:
        url = os.environ["ORCHESTRATOR_URL"]
        token = os.environ["RUN_TOKEN"]
    except KeyError as e:
        sys.exit(f"bus_client: required env var {e} is not set (see launch.sh / .env)")
    return {
        "url": url,
        "token": token,
        "run_id": os.environ.get("RUN_ID"),
        "role": os.environ.get("AGENT_ROLE", "main"),
        "team": os.environ.get("AGENT_TEAM"),
        "repo": os.environ.get("AGENT_REPO"),
        "parent": os.environ.get("AGENT_PARENT"),
    }


async def _register(conn, cfg: dict) -> dict:
    await conn.send(json.dumps({
        "type": "register", "role": cfg["role"], "team": cfg["team"],
        "repo": cfg["repo"], "parent": cfg["parent"], "run_id": cfg["run_id"],
        "token": cfg["token"],
    }))
    reply = json.loads(await conn.recv())
    if reply.get("type") != "registered":
        raise SystemExit(f"bus_client: registration refused: {reply}")
    return reply


async def run(announce_only: bool) -> None:
    cfg = _cfg()
    async with websockets.connect(cfg["url"], max_size=MAX_PAYLOAD_BYTES) as conn:
        reg = await _register(conn, cfg)
        addr = reg["address"]
        print(f"bus_client: registered as {addr} "
              f"(peers: {', '.join(reg.get('allowed_peers') or []) or 'none yet'})",
              flush=True)

        if announce_only:
            if cfg["parent"]:
                await conn.send(json.dumps({
                    "from": addr, "to": cfg["parent"], "type": "status",
                    "payload": {"state": "up"}, "run_id": cfg["run_id"],
                }))
            return

        # Connected on startup; now listen. Received messages are DATA, printed
        # for the agent to reason about. Nothing here executes a payload.
        async for raw in conn:
            try:
                msg = json.loads(raw)
            except ValueError:
                print(f"bus_client: dropped non-JSON frame ({len(raw)} bytes)", flush=True)
                continue
            print("bus_client: inbound " + json.dumps(msg, ensure_ascii=False), flush=True)


def main() -> None:
    ap = argparse.ArgumentParser(description="Connect to the orchestrator and exchange messages.")
    ap.add_argument("--announce", action="store_true",
                    help="register, send one status message to the parent, then exit")
    args = ap.parse_args()
    try:
        asyncio.run(run(args.announce))
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
