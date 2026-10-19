#!/usr/bin/env bash
# start-experiment.sh: One command to set up and run the full experiment
# Sets up repos, installs dependencies, and starts the orchestrator connection.

set -euo pipefail
cd "$(dirname "$0")"

echo "Starting experiment setup..."
bash ./setup.sh
echo "✓ Repos initialized"

echo "Starting orchestrator connection..."
uv venv .bus-venv 2>/dev/null || true
uv pip install --python .bus-venv/bin/python websockets==12.0 -q

.bus-venv/bin/python ./bus_client.py >.bus-client.log 2>&1 &
BUS_PID=$!
echo $BUS_PID > .bus-client.pid

sleep 2
if grep -q "registered as main" .bus-client.log; then
  echo "✓ Orchestrator connected (pid $BUS_PID)"
else
  echo "✗ Orchestrator connection failed - check .bus-client.log"
  kill $BUS_PID 2>/dev/null || true
  exit 1
fi

echo ""
echo "✓ Experiment ready. Now run: ./launch.sh"
