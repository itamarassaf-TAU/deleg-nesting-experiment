#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
ROOT="$(pwd -P)"

command -v python3 >/dev/null || { echo "python3 is required" >&2; exit 1; }
command -v claude >/dev/null || {
  echo "Claude CLI is required and must already be authenticated." >&2
  exit 1
}

if [[ ! -f .env ]]; then
  cp .env.example .env
  echo "Created .env. Set TELEGRAM_API_TOKEN and TELEGRAM_ALLOWED_USER_IDS, then rerun." >&2
  exit 1
fi

VENV="$ROOT/.telegram-venv"
python3 -m venv "$VENV"
"$VENV/bin/python" -m pip install -r requirements.txt
bash setup.sh
./validate_manifest.sh
"$VENV/bin/python" telegram_comunication.py --validate-config
exec ./scripts/start-telegram.sh
