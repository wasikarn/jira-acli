#!/usr/bin/env python3
"""adf-node-diff — count / diff ADF structural nodes. Safety gate for a full-body
description or Confluence-page replace (the same manual check used to catch the
table-flattening incident in ISSUES.md Issue 5, now a script instead of a fresh
inline snippet each time).

Usage:
  python3 adf-node-diff.py desc.json                              # single file: node-type counts
  acli jira workitem view KEY --json | python3 adf-node-diff.py -  # same, piped straight from acli
  python3 adf-node-diff.py before.json after.json                 # diff: counts + delta + byte-exact check

Accepts either a bare ADF doc (`{"type": "doc", ...}`) or a full acli/MCP view
payload (extracts `fields.description` automatically) — mix and match across the
two file args, e.g. a locally-built patch (bare doc) vs. a live `view --json`
payload after writing it.

Single-file mode: run on the CURRENT live description before any full-body
replace — a non-zero `table`/`extension`/`panel`/`expand` count means the parser
doing the replace (md2adf.py) may not round-trip that node type; see SKILL.md
"Description format" for which types it currently handles.

Diff mode: run with (intended patch, post-write live doc) to confirm the write
landed exactly as sent. Byte-exact is the strongest possible confirmation — a
node-type count match alone can hide a text-content change inside an unchanged
node count. Diffing (old live doc, new intended patch) instead shows what's
about to change — a non-zero delta there is often expected (that's the edit);
the point is to eyeball that nothing unintended moved.
"""
import argparse
import json
import sys
from collections import Counter


def count_nodes(node, counter=None):
    if counter is None:
        counter = Counter()
    if isinstance(node, dict):
        t = node.get("type")
        if t:
            counter[t] += 1
        for child in node.get("content", []) or []:
            count_nodes(child, counter)
    elif isinstance(node, list):
        for child in node:
            count_nodes(child, counter)
    return counter


def extract_doc(data, label):
    if isinstance(data, dict) and data.get("type") == "doc":
        return data
    if isinstance(data, dict) and "fields" in data:
        desc = data["fields"].get("description")
        if not isinstance(desc, dict):
            sys.exit(f"FATAL: {label}: fields.description is not an ADF doc (empty/plain-text description?)")
        return desc
    sys.exit(f"FATAL: {label}: unrecognized input — expected an ADF doc or an acli view payload with fields.description")


def load(path, label):
    raw = sys.stdin.read() if path == "-" else open(path, encoding="utf-8").read()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        sys.exit(f"FATAL: {label}: invalid JSON: {e}")
    return extract_doc(data, label)


def print_counts(doc):
    counts = count_nodes(doc)
    if not counts:
        print("(no structural nodes found)")
        return
    for t in sorted(counts):
        print(f"{t}: {counts[t]}")


def print_diff(doc1, doc2):
    c1, c2 = count_nodes(doc1), count_nodes(doc2)
    types = sorted(set(c1) | set(c2))
    width = max((len(t) for t in types), default=4)
    print(f"{'type'.ljust(width)}  OLD  NEW  Δ")
    changed = 0
    for t in types:
        a, b = c1.get(t, 0), c2.get(t, 0)
        delta = b - a
        if delta != 0:
            changed += 1
        sign = f"+{delta}" if delta > 0 else str(delta)
        marker = "  <-- changed" if delta != 0 else ""
        print(f"{t.ljust(width)}  {a:>3}  {b:>3}  {sign:>4}{marker}")
    exact = json.dumps(doc1, sort_keys=True) == json.dumps(doc2, sort_keys=True)
    print()
    print(f"byte-exact match: {'YES' if exact else 'NO'} ({changed} node type{'s' if changed != 1 else ''} changed)")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file1", nargs="?", default="-", help="ADF doc or acli view payload; '-'/omitted for stdin")
    ap.add_argument("file2", nargs="?", help="second file — switches to diff mode")
    args = ap.parse_args()

    doc1 = load(args.file1, "file1")
    if args.file2:
        doc2 = load(args.file2, "file2")
        print_diff(doc1, doc2)
    else:
        print_counts(doc1)


if __name__ == "__main__":
    main()
