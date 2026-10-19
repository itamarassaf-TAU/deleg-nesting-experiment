# RUNME: from clone to result

All paths are relative to the repo root. Nothing here depends on where you clone it.

**Requirements:** git, Python 3.12 (`python3.12` on PATH, or installed through `uv`), network access to PyPI (each `check.sh` installs pytest), and Claude Code.

## 1. Clone and set up (once)

```bash
git clone https://github.com/itamarassaf-TAU/deleg-nesting-experiment.git
cd deleg-nesting-experiment
bash setup.sh                 # builds .localgit/<team>/<repo> and manifest.json for THIS location
./validate_manifest.sh        # expect 4 × OK
```

`setup.sh` is idempotent. Re-run it whenever you move or re-clone the directory, because `manifest.json` holds absolute `file://` URLs for the current location.

## 2. Pre-allow permissions

Subagents can't answer permission prompts, so every tool call they make must already be allowed. Choose one:

- **A. Auto mode (default).** `./launch.sh` starts Claude Code with `--permission-mode auto`. Nothing else is needed.
- **B. Explicit allowlist.** Add this next to `"hooks"` in `.claude/settings.json`, then launch without `--permission-mode`:

  ```json
  "permissions": {
    "allow": [
      "Agent", "Task",
      "Read", "Grep", "Glob",
      "Write(reports/**)", "Edit(reports/**)",
      "Bash(git clone file://*)",
      "Bash(bash */check.sh)", "Bash(./check.sh)",
      "Bash(rm -rf work/*)", "Bash(mkdir:*)", "Bash(cd:*)",
      "Bash(grep:*)", "Bash(ls:*)", "Bash(cat:*)", "Bash(tail:*)", "Bash(pwd)"
    ]
  }
  ```

  Agents phrase commands in many ways, so watch the first minute of the run and add a rule for any call that gets stuck waiting for approval.

Don't use `dontAsk` mode or headless `claude -p` without an allowlist. Unapproved calls are then *denied*, and a repo looks like it failed when the cause was a blocked permission.

## 3. Launch with the caps forced open

```bash
./launch.sh --dry-run   # pre-flight only: manifest matches this location, log/reports/work are empty
./launch.sh
```

`launch.sh` runs this, after the pre-flight checks:

```bash
CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=3 CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS=32 claude --permission-mode auto
```

- **Depth 3:** the run needs depth ≥ 2 (main → team → repo). The default can change server-side, so it's set explicitly instead of relying on it.
- **Concurrency 32:** a fully parallel run is 4 team agents plus 24 repo agents, 28 in total. The default limit is 20, and spawns over the limit are **rejected, not queued**. The parent then audits those repos itself and they drop out of the tree.

Launch from the repo root. The PreToolUse hook in `.claude/settings.json` only loads for sessions rooted here. If Claude Code asks you to trust the folder or approve its hooks, accept.

## 4. Watch the spawn log

In a second terminal:

```bash
tail -f spawn-log.ndjson
# compact view:
tail -f spawn-log.ndjson | python3 -u -c 'import json,sys; [print(r["ts"][11:23], r["tool"].ljust(6), r.get("agent_id","main").ljust(18), r["input"][:80]) for r in map(json.loads, sys.stdin)]'
```

The hook logs one line per Agent/Task/Bash call. A line without `agent_id` came from the main session.

## 5. Start the audit

Paste the full contents of `KICKOFF_PROMPT.md` into the session.

## 6. Results

- `reports/<team>.md`: one report per team, plus a roll-up table printed in the session.
- `spawn-log.ndjson`: the spawn/command tree.
- Grade against `grading/answer-key.json` **after** the run.

## Reset for another run

```bash
rm -rf work reports/*.md && : > spawn-log.ndjson && bash setup.sh
```
