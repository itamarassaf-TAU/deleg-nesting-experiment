# Run the experiment

All paths are relative to the repository root.

## Setup

```bash
git clone https://github.com/itamarassaf-TAU/deleg-nesting-experiment.git
cd deleg-nesting-experiment
./bootstrap.sh
```

Configure `.env` before running `./bootstrap.sh`. Use
`./bootstrap.sh --dry-run` to inspect setup actions.

## Audit

```bash
./scripts/start-audit.sh
```

Use `./launch.sh --dry-run` to run the audit pre-flight only.
Use `./scripts/show-audit-prompt.sh` to print the audit prompt.

## Results

Team reports are written under `reports/`. Runtime output is written under
`work/` and `spawn-log.ndjson`.

