# Run the experiment

All paths are relative to the repository root.

## Setup and Launch

```bash
git clone https://github.com/itamarassaf-TAU/deleg-nesting-experiment.git
cd deleg-nesting-experiment
./start-experiment.sh
./launch.sh
```

**Configure `.env` before running `./start-experiment.sh`** (sets `ORCHESTRATOR_URL` and `RUN_TOKEN`).

The `./start-experiment.sh` script:
- Initializes local git repos (via `setup.sh`)
- Installs orchestrator dependencies
- Starts the bus_client connection to the orchestrator
- Validates the connection is live

Then paste the contents of `KICKOFF_PROMPT.md` into the interactive `./launch.sh` session.

### Debugging

- Use `./launch.sh --dry-run` to run pre-flight checks only
- Check `.bus-client.log` for orchestrator connection details
- Use `./scripts/show-audit-prompt.sh` to print the audit prompt

## Results

Team reports are written under `reports/`. Runtime output is written under
`work/` and `spawn-log.ndjson`.

