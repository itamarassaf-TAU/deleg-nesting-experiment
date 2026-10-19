# deleg-nesting-experiment

Follow [RUNME.md](RUNME.md) to operate the experiment.

## Quick start

After cloning, configure `.env` and run:

```bash
./bootstrap.sh
```

Use these commands to manage the Telegram bridge:

```bash
./scripts/status.sh
./scripts/stop.sh
./scripts/start-telegram.sh
```

Run the audit with:

```bash
./scripts/start-audit.sh
```

Use [.env.example](.env.example) as the configuration template.
