#!/usr/bin/env python3
"""Self-check for adf-node-diff.py. No framework — run directly: python3 test_adf_node_diff.py"""
import importlib.util
import sys
from pathlib import Path

spec = importlib.util.spec_from_file_location("adf_node_diff", Path(__file__).parent / "adf-node-diff.py")
assert spec and spec.loader
adf_node_diff = importlib.util.module_from_spec(spec)
spec.loader.exec_module(adf_node_diff)
count_nodes, extract_doc = adf_node_diff.count_nodes, adf_node_diff.extract_doc

DOC_WITH_TABLE = {
    "type": "doc", "version": 1,
    "content": [
        {"type": "heading", "attrs": {"level": 2}, "content": [{"type": "text", "text": "H"}]},
        {"type": "paragraph", "content": [{"type": "text", "text": "p"}]},
        {"type": "table", "attrs": {}, "content": [
            {"type": "tableRow", "content": [
                {"type": "tableHeader", "attrs": {}, "content": [{"type": "paragraph", "content": [{"type": "text", "text": "a"}]}]},
            ]},
        ]},
    ],
}


def test_count_nodes_basic():
    c = count_nodes(DOC_WITH_TABLE)
    assert c["heading"] == 1
    assert c["table"] == 1
    assert c["tableRow"] == 1
    assert c["tableHeader"] == 1
    assert c["paragraph"] == 2  # top-level + the one inside tableHeader


def test_count_nodes_empty_doc():
    c = count_nodes({"type": "doc", "version": 1, "content": []})
    assert c["doc"] == 1
    assert sum(c.values()) == 1


def test_extract_doc_bare():
    d = extract_doc(DOC_WITH_TABLE, "x")
    assert d is DOC_WITH_TABLE


def test_extract_doc_from_view_payload():
    payload = {"key": "TP-1", "fields": {"description": DOC_WITH_TABLE}}
    d = extract_doc(payload, "x")
    assert d is DOC_WITH_TABLE


def test_extract_doc_rejects_plain_string_description():
    payload = {"key": "TP-1", "fields": {"description": "plain text, not ADF"}}
    try:
        extract_doc(payload, "x")
        assert False, "should have exited on non-ADF description"
    except SystemExit:
        pass


def test_diff_detects_dropped_table():
    without_table = {"type": "doc", "version": 1, "content": [DOC_WITH_TABLE["content"][0], DOC_WITH_TABLE["content"][1]]}
    c_before, c_after = count_nodes(DOC_WITH_TABLE), count_nodes(without_table)
    assert c_before["table"] == 1
    assert c_after.get("table", 0) == 0  # exactly the table-flattening incident this tool exists to catch


def test_diff_byte_exact_on_identical_docs():
    import copy
    import json
    a, b = DOC_WITH_TABLE, copy.deepcopy(DOC_WITH_TABLE)
    assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)


if __name__ == "__main__":
    tests = [v for k, v in list(globals().items()) if k.startswith("test_")]
    failed = 0
    for t in tests:
        try:
            t()
            print(f"ok   {t.__name__}")
        except AssertionError as e:
            failed += 1
            print(f"FAIL {t.__name__}: {e}")
    print(f"\n{len(tests) - failed}/{len(tests)} passed")
    sys.exit(1 if failed else 0)
