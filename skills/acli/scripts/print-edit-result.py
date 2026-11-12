#!/usr/bin/env python3
"""print-edit-result — pretty-print the first result of an `acli ... edit --json` response.

Usage: acli jira workitem edit --from-json ... --json | python3 print-edit-result.py
"""
import json
import sys

raw = sys.stdin.read()
try:
    r = json.loads(raw)["results"][0]
    print(r["status"], "-", r["message"])
except (ValueError, KeyError, IndexError, TypeError):
    sys.exit("FATAL: unexpected edit response (no results[0].status/message): " + raw[:500])
