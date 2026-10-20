# deleg-nesting-experiment

Follow [RUNME.md](RUNME.md) to operate the experiment.

## Quick start

After cloning:

1. Create the client venv (once):

   ```bash
   uv venv .bus-venv && uv pip install --python .bus-venv/bin/python websockets==12.0
   ```

2. Point `.env` at the orchestrator (ask the operator for the token):

   ```
   ORCHESTRATOR_URL=ws://<ORCHESTRATOR_HOST>:8080
   RUN_TOKEN=<token>
   ```

3. Join the orchestrator (stays connected and listens):

   ```bash
   AGENT_ROLE=team-agent AGENT_TEAM=payments AGENT_PARENT=main python3 ./bus_client.py
   ```

Run the audit with:

```bash
./launch.sh      # or ./scripts/start-audit.sh, which just calls launch.sh
```

Use [.env.example](.env.example) as the configuration template.
