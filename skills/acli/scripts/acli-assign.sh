#!/usr/bin/env bash
# acli-assign.sh — assign a Jira work item by accountId.
#
# `acli jira workitem assign --assignee <accountId>` silently UNassigns instead
# (it only resolves @me/default/email — a raw accountId is misread and clears the
# field). `edit --from-json` resolves the same accountId correctly, so this routes
# through that instead (verified 2026-07-15 against two different accountIds).
#
# For @me/default/email, just use `acli jira workitem assign` directly — this
# script is only for the accountId case.
set -euo pipefail

if [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ] || [ $# -lt 2 ]; then
  echo "usage: acli-assign.sh KEY ACCOUNT_ID" >&2
  echo "  for email/@me/default assignee, use: acli jira workitem assign --key KEY --assignee ..." >&2
  exit 1
fi

KEY="$1"
ACCOUNT_ID="$2"

tmp_payload=$(mktemp)
trap 'rm -f "$tmp_payload"' EXIT

python3 -c "
import json, sys
json.dump({'issues': [sys.argv[1]], 'assignee': sys.argv[2]}, open(sys.argv[3], 'w'))
" "$KEY" "$ACCOUNT_ID" "$tmp_payload"

acli jira workitem edit --from-json "$tmp_payload" --yes --json \
  | python3 -c "import json,sys; r=json.load(sys.stdin)['results'][0]; print(r['status'], '-', r['message'])"
