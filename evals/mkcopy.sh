#!/usr/bin/env bash
# Builds an eval copy of jira-acli: HEAD's tracked files plus the working tree's evals/, with defaultEnabled true
# (claude plugin eval runs the with-arm without a plugin whose manifest sets defaultEnabled false).
set -euo pipefail
repo="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
dest=${1:?usage: mkcopy.sh <dest dir>}
mkdir -p "$dest"
git -C "$repo" archive HEAD | tar -x -C "$dest"
cp -R "$repo/evals" "$dest/"
python3 - "$dest/.claude-plugin/plugin.json" <<'EOF'
import json, sys
p = sys.argv[1]
m = json.load(open(p))
assert m["defaultEnabled"] is False
m["defaultEnabled"] = True
json.dump(m, open(p, "w"), indent=2)
print("defaultEnabled ->", json.load(open(p))["defaultEnabled"], "version", m["version"])
EOF
