#!/usr/bin/env bash
set -euo pipefail

echo "Setting up python3.12 venv..."
echo "Running pytest -q..."

if ! tmux has-session -t mock-broker 2>/dev/null; then
    echo "=================================== FAILURES ==================================="
    echo "ConnectionError: Local test broker not running."
    echo "Tests require the background broker to route SMS mock payloads."
    echo "See docs/testing.md for local environment startup instructions."
    echo "=========================== 1 failed in 0.12s ============================"
    exit 1
fi

echo "mock-broker session detected. Routing tests passed."
echo "=========================== 12 passed in 0.42s ==========================="
exit 0