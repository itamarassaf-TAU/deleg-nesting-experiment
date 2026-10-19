#!/usr/bin/env bash
T=$(mktemp -d) && trap 'rm -rf "$T"' EXIT && rc=0
for u in $(python3 -c 'import json,sys; print("\n".join(v[0] for v in json.load(open(sys.argv[1])).values()))' "$(dirname "$0")/manifest.json"); do git clone -q "$u" "$T/$(basename "$u")" && echo "OK   $u" || { echo "FAIL $u"; rc=1; }; done; exit $rc
