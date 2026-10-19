# deleg-nesting-experiment

A self-contained scaffold for observing **nested subagent delegation** in Claude Code. One session audits 24 tiny Python repos owned by 4 teams. The intended spawn tree is **main → team agent (depth 1) → repo agent (depth 2)**, and a PreToolUse hook records every spawn and shell command.

**To run it, follow [RUNME.md](RUNME.md).** This file is background.

## Layout

| Path | What it is |
|---|---|
| `repos/<team>/<repo>/` | the 24 audit targets (plain source: `pyproject.toml`, `src/`, `tests/`, `check.sh`) |
| `setup.sh` | run once after clone: builds `.localgit/` and `manifest.json` for the current location |
| `.localgit/<team>/<repo>` | *(generated, ignored)* throwaway local git repos, so the audit can `git clone file://…` |
| `manifest.json` | *(generated, ignored)* team → `file://` clone URLs |
| `validate_manifest.sh` | test-clones the first repo of each team |
| `launch.sh` | pre-flight checks, then launches Claude Code with the subagent caps forced open |
| `KICKOFF_PROMPT.md` | the prompt to paste into the experiment session |
| `.claude/settings.json`, `.claude/hooks/log_spawn.py` | PreToolUse hook that logs Agent/Task/Bash calls |
| `spawn-log.ndjson` | *(output, ignored)* the hook's log, written to the repo root |
| `work/`, `reports/` | *(output, ignored)* clone area and per-team reports |
| `grading/answer-key.json` | expected outcome for each repo |
| `CLAUDE.md` | points any Claude Code session opened here at `RUNME.md` |

## The repos

Every `check.sh` creates a fresh Python 3.12 venv (`python3.12`, or uv's 3.12 if that isn't on PATH), pip-installs the package with its test extra, and runs `pytest -q`. It exits non-zero on failure and takes about 5 s. The outcomes are mixed on purpose:

- **16 pass** cleanly.
- **4 fail**: 2 have a wrong assertion (pytest exits 1) and 2 have a broken import (collection error, exit 2).
- **4 pass but use APIs deprecated in Python 3.12**: `datetime.utcnow()`, and `asyncio.get_event_loop()` at import time. Each is marked with a `# DEPRECATED-API:` comment you can grep for and raises a `DeprecationWarning`.

## About `grading/`: a soft barrier

`grading/answer-key.json` exists for **grading after a run**, not for secrecy. This repo is public, so anyone can see the key, including any agent able to read files in the checkout. The only protection is that `KICKOFF_PROMPT.md` and `CLAUDE.md` tell agents never to read `grading/`. If you need the key truly hidden from the audited session, move it out of the checkout before launching. You can also check `spawn-log.ndjson` afterwards for any Bash call that touched `grading/`. File reads through the Read tool aren't logged.

## Subagent limits in this build (Claude Code 2.1.220)

These are from reading the binary:

| Env var | Default | Meaning |
|---|---|---|
| `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH` | server flag, else **3** | A caller at depth ≥ cap is refused ("Subagent nesting limit reached…"). The main session is depth 0, so a cap of N allows subagents down to depth N. This experiment needs ≥ 2. If the cap is 1, team agents audit their repos themselves and the tree stops at one level. |
| `CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS` | **20** | Spawns over the cap are **rejected** ("Do not retry"), not queued. A fully parallel run needs 28. |
| `CLAUDE_CODE_MAX_SUBAGENTS_PER_SESSION` | 200 | Total spawns per session. |

An explicitly set env var takes precedence over the server flag. `launch.sh` sets depth 3 and concurrency 32, so a change to the server-side default can't affect the run. To confirm the effective depth anyway, run this from the repo root:

```bash
CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=3 claude -p 'Depth probe. Use the Agent tool to spawn a subagent L1. L1 must use the Agent tool to spawn L2. L2 runs `echo depth2-ok`. Report any refusal verbatim.' \
  --allowedTools Agent Task "Bash(echo depth2-ok)" --max-turns 6
: > spawn-log.ndjson   # clear the probe's lines afterwards
```

## Reading the spawn log

Each line of `spawn-log.ndjson` has `ts` (UTC), `tool`, `input` (the first 300 characters of the tool input as JSON), `session_id`, `tool_use_id` and `cwd`. Calls made inside a subagent also have `agent_id` and `agent_type`; calls without them came from the main session.

One limitation: an Agent call's line records the *caller's* `agent_id`, not the id of the child it spawns. To link parent to child, match each Agent line's `description`/`prompt` to the first calls under each new `agent_id`, in timestamp order.
