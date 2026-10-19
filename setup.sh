#!/usr/bin/env bash
# Run once after cloning. Idempotent: wipes and rebuilds .localgit/ and manifest.json every time.
#  - turns each repos/<team>/<repo> into a throwaway local git repo at .localgit/<team>/<repo> (branch main)
#  - writes manifest.json: team -> file:// clone URLs computed from the CURRENT location
set -euo pipefail
cd "$(dirname "$0")"
ROOT="$(pwd -P)"

rm -rf ./.localgit
mkdir -p .localgit reports
for src in repos/*/*/; do
  src="${src%/}"; team="$(basename "$(dirname "$src")")"; repo="$(basename "$src")"
  dst=".localgit/$team/$repo"
  git init -q --bare -b main "$dst"
  g=(git --git-dir="$dst" --work-tree="$src" -c user.name=deleg-exp -c user.email=deleg-exp@localhost)
  "${g[@]}" add -A
  GIT_AUTHOR_DATE="2026-01-01T00:00:00Z" GIT_COMMITTER_DATE="2026-01-01T00:00:00Z" "${g[@]}" commit -q -m "Initial commit"
  rm -f "$dst/index"
done

python3 - "$ROOT" <<'PY'
import json, sys
from pathlib import Path
root = Path(sys.argv[1])
m = {t.name: [r.as_uri() for r in sorted(t.iterdir()) if r.is_dir()]
     for t in sorted((root / ".localgit").iterdir()) if t.is_dir()}
(root / "manifest.json").write_text(json.dumps(m, indent=2) + "\n")
print(f"setup: {sum(map(len, m.values()))} repos in {len(m)} teams -> manifest.json ({root})")
PY
