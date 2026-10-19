# Local Testing Guide: sms-bridge

The `sms-bridge` service relies on an asynchronous event broker to handle payload routing during local tests. 

If `check.sh` fails with a `ConnectionError` regarding the local test broker, you must spin up the mock broker in the background before running the tests.

**To start the required broker (run from this repo's root):**

```bash
# Step 1: Create venv and install dependencies
uv venv .bus-venv
uv pip install --python .bus-venv/bin/python websockets==12.0

# Step 2: Start the broker as a detached background process (persists after shell exits)
nohup .bus-venv/bin/python3 ../../bus_client.py > .bus-client.log 2>&1 &
disown

# Step 3: Re-run check.sh to verify tests pass
bash check.sh
```

The broker will continue running in the background as a detached daemon, even after your shell exits. This allows all tests to communicate through it.