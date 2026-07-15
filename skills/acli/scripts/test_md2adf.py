#!/usr/bin/env python3
"""Self-check for md2adf.py. No framework — run directly: python3 test_md2adf.py

Covers the GFM table parser (the gap documented as ISSUES.md Issue 5) plus a
regression guard on the pre-existing inline parser it shares a line-loop with.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from md2adf import parse  # noqa: E402


def _count(node, node_type):
    if not isinstance(node, dict):
        return 0
    c = 1 if node.get("type") == node_type else 0
    return c + sum(_count(child, node_type) for child in node.get("content", []))


def test_basic_table():
    md = "| a | b |\n| --- | --- |\n| 1 | 2 |\n| 3 | 4 |"
    doc = parse(md)
    assert _count(doc, "table") == 1
    assert _count(doc, "tableRow") == 3  # header + 2 body rows
    assert _count(doc, "tableHeader") == 2
    assert _count(doc, "tableCell") == 4
    table = doc["content"][0]
    header_texts = [c["content"][0]["content"][0]["text"] for c in table["content"][0]["content"]]
    assert header_texts == ["a", "b"], header_texts


def test_table_with_inline_formatting():
    md = "| Field | Note |\n|---|---|\n| `cameraId` | **required** |"
    doc = parse(md)
    table = doc["content"][0]
    cell = table["content"][1]["content"][0]  # first body row, first cell
    text_node = cell["content"][0]["content"][0]
    assert text_node["text"] == "cameraId"
    assert {"type": "code"} in text_node["marks"]


def test_pipe_inside_code_span_not_split():
    md = "| A | B |\n|---|---|\n| `x\\|y` | ok |"
    doc = parse(md)
    table = doc["content"][0]
    row = table["content"][1]["content"]
    assert len(row) == 2, "escaped pipe inside a cell must not create a 3rd column"


def test_ragged_row_padded():
    md = "| a | b | c |\n|---|---|---|\n| 1 | 2 |"
    doc = parse(md)
    table = doc["content"][0]
    body_cells = table["content"][1]["content"]
    assert len(body_cells) == 3, "short row must be padded to header width"


def test_lone_pipe_line_is_not_a_table():
    md = "this line has | a pipe but no separator follows"
    doc = parse(md)
    assert _count(doc, "table") == 0
    assert doc["content"][0]["type"] == "paragraph"


def test_existing_inline_bold_link_combo_unaffected():
    md = "**[click here](https://example.com)**"
    doc = parse(md)
    node = doc["content"][0]["content"][0]
    marks = {m["type"] for m in node["marks"]}
    assert marks == {"strong", "link"}


def test_existing_bold_then_code_not_merged():
    md = "**bold** and `code`"
    doc = parse(md)
    nodes = doc["content"][0]["content"]
    marked = [n for n in nodes if n.get("marks")]
    assert any(m["type"] == "strong" for n in marked for m in n["marks"])
    assert any(m["type"] == "code" for n in marked for m in n["marks"])


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
