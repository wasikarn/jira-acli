#!/usr/bin/env bash
# acli-ls.sh — render a JQL query or key-list as an aligned table.
#
# Wraps `acli jira workitem search --json | acli-ls.py`, the most-rewritten
# acli-adjacent pattern in real usage (40+ inline reinventions). The python side
# bakes in the list-or-dict unwrap + nested-field guards everyone re-derives.
#
# Usage:
#   bash acli-ls.sh --jql "project = TP AND statusCategory != Done"
#   bash acli-ls.sh --key TP-1,TP-2,TP-3        # convenience: becomes key IN (...) ORDER BY key
#   bash acli-ls.sh --filter 10001
# Columns: key · type · status · assignee · summary.
# NOTE: `parent` used to be a column here but acli's `search --fields` unconditionally
# rejects it ("field 'parent' is not allowed", confirmed 1.3.22-stable, ISSUES.md Issue 7)
# regardless of JQL/issue type — for a single key's parent, use `view --fields parent` instead.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
FIELDS="key,summary,status,issuetype,assignee"

JQL="" ; FILTER="" ; KEYS=""
while [ $# -gt 0 ]; do
  case "$1" in
    --jql)    JQL="$2"; shift 2 ;;
    --filter) FILTER="$2"; shift 2 ;;
    --key)    KEYS="$2"; shift 2 ;;
    -h|--help) sed -n '2,13p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "acli-ls: unknown arg: $1" >&2; exit 2 ;;
  esac
done

if [ -n "$KEYS" ]; then
  # comma/space list → key IN (a,b,c) ORDER BY key
  JQL="key IN (${KEYS// /,}) ORDER BY key ASC"
fi

if [ -n "$JQL" ]; then
  acli jira workitem search --jql "$JQL" --fields "$FIELDS" --paginate --json | python3 "$HERE/acli-ls.py"
elif [ -n "$FILTER" ]; then
  acli jira workitem search --filter "$FILTER" --fields "$FIELDS" --paginate --json | python3 "$HERE/acli-ls.py"
else
  echo "acli-ls: need --jql, --key, or --filter" >&2
  exit 2
fi
