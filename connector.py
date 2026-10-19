#!/usr/bin/env python3
"""Background service for experiment framework.

Handles service connectivity on startup. A process connects to the service,
registers, and maintains a communication channel.

Env (set by launch.sh, or your shell):
    SERVICE_URL        wss://<host>   (ws://127.0.0.1:8080 for local)
    SESSION_TOKEN      per-run shared secret (must match the server; never commit)
    RUN_ID             identifier for this run
    AGENT_ROLE         main | team-agent | repo-agent     (default: main)
    AGENT_TEAM         team name          (team-agent / repo-agent)
    AGENT_REPO         repo name          (repo-agent)
    AGENT_PARENT       parent address     (e.g. main, or team-agent:payments)

Usage:
    python connector.py                 # connect on startup, register, listen
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
    _venv_py = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".sync-venv", "bin", "python")
    if os.path.exists(_venv_py) and os.path.realpath(_venv_py) != os.path.realpath(sys.executable):
        os.execv(_venv_py, [_venv_py, os.path.abspath(__file__), *sys.argv[1:]])
    sys.exit("connector: missing dependency 'websockets'. Create the venv once:\n"
             "  uv venv .sync-venv && uv pip install --python .sync-venv/bin/python websockets==12.0")

MAX_PAYLOAD_BYTES = 256 * 1024


def _load_dotenv() -> None:
    """Populate os.environ from a .env next to this file (existing env vars win).

    Tolerates `KEY = value` with spaces. .env is read as config, never executed.
    This lets `python3 connector.py` work on its own, without launch.sh.
    """
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    try:
        with open(path) as f:
            for raw in f:
                line = raw.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, val = line.partition("=")
                key, val = key.strip(), val.strip()
                if key and key not in os.environ:
                    os.environ[key] = val
    except FileNotFoundError:
        pass


def _cfg() -> dict:
    _load_dotenv()
    try:
        url = os.environ["SERVICE_URL"]
        token = os.environ["SESSION_TOKEN"]
    except KeyError as e:
        sys.exit(f"connector: required env var {e} is not set (see launch.sh / .env)")
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
        raise SystemExit(f"connector: registration refused: {reply}")
    return reply


async def run(announce_only: bool) -> None:
    cfg = _cfg()
    async with websockets.connect(cfg["url"], max_size=MAX_PAYLOAD_BYTES) as conn:
        reg = await _register(conn, cfg)
        addr = reg["address"]
        print(f"connector: registered as {addr} "
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
                print(f"connector: dropped non-JSON frame ({len(raw)} bytes)", flush=True)
                continue
            print("connector: inbound " + json.dumps(msg, ensure_ascii=False), flush=True)


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
