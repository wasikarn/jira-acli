#!/usr/bin/env python3
"""Self-check for acli-edit.py. No framework — run directly: python3 test_acli_edit.py"""
import importlib.util
import json
import sys
import tempfile
from pathlib import Path

spec = importlib.util.spec_from_file_location("acli_edit", Path(__file__).parent / "acli-edit.py")
assert spec and spec.loader
acli_edit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(acli_edit)

OLD = {"type": "doc", "version": 1, "content": [{"type": "paragraph", "content": [{"type": "text", "text": "OLD"}]}]}
NEW = {"type": "doc", "version": 1, "content": [{"type": "paragraph", "content": [{"type": "text", "text": "NEW"}]}]}


def _run(cur, key="X-1", mode="append"):
    """Run merge() on files; return (payload or None, exit message or None)."""
    d = Path(tempfile.mkdtemp())
    (d / "cur.json").write_text(json.dumps(cur))
    (d / "new.json").write_text(json.dumps(NEW))
    out = d / "payload.json"
    try:
        acli_edit.merge(mode, key, d / "cur.json", out, d / "new.json", "")
    except SystemExit as e:
        return (json.loads(out.read_text()) if out.exists() else None), str(e.code)
    return json.loads(out.read_text()), None


def _texts(payload):
    return [n["content"][0]["text"] for n in payload["description"]["content"]]


def test_append_keeps_existing_description():
    payload, err = _run({"key": "X-1", "fields": {"description": OLD}})
    assert err is None, err
    assert _texts(payload) == ["OLD", "NEW"]


def test_append_to_empty_description_is_allowed():
    payload, err = _run({"key": "X-1", "fields": {"description": None}})
    assert err is None, err
    assert _texts(payload) == ["NEW"]


def test_view_of_another_issue_fails_loud_without_payload():
    payload, err = _run({"key": "Y-9", "fields": {"description": OLD}})
    assert payload is None, "a payload for the wrong issue would replace X-1's description"
    assert err and err.startswith("FATAL:") and "Y-9" in err


def test_dict_without_fields_fails_loud_without_payload():
    payload, err = _run({"issues": [{"key": "X-1", "fields": {"description": OLD}}]})
    assert payload is None, "an unknown view shape must not become an empty description"
    assert err and err.startswith("FATAL:")


def test_list_item_without_fields_fails_loud():
    payload, err = _run([{"key": "X-1"}])
    assert payload is None
    assert err and err.startswith("FATAL:")


def test_bare_adf_doc_is_used_as_the_description():
    # jira-content SKILL.md documents a local bare doc as CUR.json for offline testing.
    payload, err = _run(OLD)
    assert err is None, err
    assert _texts(payload) == ["OLD", "NEW"]


def test_key_match_ignores_case():
    payload, err = _run({"key": "X-1", "fields": {"description": OLD}}, key="x-1")
    assert err is None, err
    assert _texts(payload) == ["OLD", "NEW"]
    payload, err = _run([{"key": "X-1", "fields": {"description": OLD}}], key="x-1")
    assert err is None, err


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    failed = 0
    for t in tests:
        try:
            t()
            print(f"PASS {t.__name__}")
        except AssertionError as e:
            failed += 1
            print(f"FAIL {t.__name__}: {e}")
    print(f"\n{len(tests) - failed}/{len(tests)} passed")
    sys.exit(1 if failed else 0)
