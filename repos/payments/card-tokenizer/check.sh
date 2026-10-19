#!/usr/bin/env bash
# Readiness check: fresh py3.12 venv -> pip install -> pytest -q. Non-zero exit on any failure.
set -euo pipefail
cd "$(dirname "$0")"
PY="$(command -v python3.12 || true)"
if [ -z "$PY" ] && command -v uv >/dev/null 2>&1; then PY="$(uv python find 3.12 2>/dev/null || true)"; fi
if [ -z "$PY" ]; then echo "check.sh: python3.12 not found" >&2; exit 2; fi
VENV=.venv-check
rm -rf "$VENV"
"$PY" -m venv "$VENV"
"$VENV/bin/pip" install -q --disable-pip-version-check ".[test]"
"$VENV/bin/python" -m pytest -q
