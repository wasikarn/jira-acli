#!/usr/bin/env python3
"""print-edit-result — pretty-print the first result of an `acli ... edit --json` response.

Usage: acli jira workitem edit --from-json ... --json | python3 print-edit-result.py
"""
import json
import sys

r = json.load(sys.stdin)["results"][0]
print(r["status"], "-", r["message"])
