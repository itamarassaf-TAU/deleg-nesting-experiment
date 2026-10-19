#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd -P)"
cat "$ROOT/KICKOFF_PROMPT.md"
