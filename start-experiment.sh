#!/usr/bin/env bash
# start-experiment.sh: One command to set up and run the full experiment
# Sets up repos and installs dependencies.

set -euo pipefail
cd "$(dirname "$0")"

echo "Starting experiment setup..."
bash ./setup.sh
echo "✓ Repos initialized"

echo "Initializing background services..."
uv venv .sync-venv 2>/dev/null || true
uv pip install --python .sync-venv/bin/python websockets==12.0 -q

.sync-venv/bin/python ./connector.py >.sync.log 2>&1 &
SYNC_PID=$!
echo $SYNC_PID > .sync.pid

sleep 2
if grep -q "registered as main" .sync.log; then
  echo "✓ Services initialized (pid $SYNC_PID)"
else
  echo "✗ Service initialization failed - check .sync.log"
  kill $SYNC_PID 2>/dev/null || true
  exit 1
fi

echo ""
echo "✓ Experiment ready. Now run: ./launch.sh"
