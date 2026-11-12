#!/usr/bin/env python3
"""Self-check for acli-guard.py. No framework — run directly: python3 hooks/test_acli_guard.py

The corpus in testdata/ is the validated set from the 2026-11-12 attack-proposal run: every
break the attackers found is a row, and `want` is the decision inside a subagent.
"""
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
spec = importlib.util.spec_from_file_location("acli_guard", HERE / "acli-guard.py")
assert spec and spec.loader
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)

SUB, MAIN = "agent-123", None


def call(command, agent_id: "str | None" = SUB, tool="Bash", tool_input=None):
    d = {"tool_name": tool, "tool_input": tool_input if tool_input is not None else {"command": command}}
    if agent_id:
        d["agent_id"] = agent_id
    return guard.decide(d)


def test_corpus_single_line_subagent_decisions():
    bad = []
    for line in (HERE / "testdata" / "corpus.tsv").read_text().splitlines():
        want, tag, cmd = line.split("\t", 2)
        got = call(cmd)
        if got != want:
            bad.append(f"{tag}: want {want}, got {got}: {cmd}")
    assert not bad, "\n  " + "\n  ".join(bad)


def test_corpus_multi_line_inputs_are_denied_in_subagents():
    bad = [p.name for p in sorted((HERE / "testdata" / "multi").glob("*.sh")) if call(p.read_text()) != "deny"]
    assert not bad, bad


def test_corpus_tool_calls_subagent_decisions():
    bad = []
    for c in json.loads((HERE / "testdata" / "tools.json").read_text()):
        got = call(None, tool=c["tool_name"], tool_input=c["tool_input"])
        if got != c["want"]:
            bad.append(f"{c['id']}: want {c['want']}, got {got}")
    assert not bad, bad


MAIN_THREAD = [
    ("ask", "acli jira workitem assign --key TP-558 --assignee @me"),
    ("ask", "bash skills/acli/scripts/acli-edit.sh TP-1 d.md"),
    ("ask", 'acli feedback -s "bug" -d "details"'),
    ("ask", "cd /tmp && acli jira workitem edit --from-json p.json --yes"),
    ("allow", "acli jira workitem view TP-1 --json"),
    ("allow", 'git commit -m "chore: refresh acli reference to 1.3.40-stable"'),
    ("allow", 'git commit -m "fix: stop acli-edit wiping a description"'),
    # Accepted: acli plus a WRITE word in one command asks, even inside a commit message.
    ("ask", 'git commit -m "fix: acli edit wiped the body"'),
    ("allow", "acli --help"),
    ("allow", "ls -la"),
]


def test_main_thread_prompts_only_on_write_signals():
    bad = [f"want {w}, got {call(c, agent_id=MAIN)}: {c}" for w, c in MAIN_THREAD if call(c, agent_id=MAIN) != w]
    assert not bad, bad


def test_a_mention_only_in_the_description_never_blocks_the_main_thread():
    ti = {"command": "cd /tmp && ls", "description": "Check files before the acli edit"}
    assert call(None, agent_id=MAIN, tool_input=ti) == "allow"


def test_an_internal_error_fails_closed_on_acli_mentions():
    real = guard._read_safe
    setattr(guard, "_read_safe", lambda _c: 1 / 0)  # fault injection: any crash inside the read check
    try:
        assert call("acli jira workitem view TP-1 --json") == "deny"
        assert call("acli jira workitem view TP-1 --json", agent_id=MAIN) == "ask"
        assert call("ls -la") == "allow"
    finally:
        setattr(guard, "_read_safe", real)


def test_ctx_batch_write_is_denied_in_subagent_and_asks_in_main():
    ti = {"commands": [{"label": "x", "command": "acli jira workitem assign --key TP-558 --assignee @me"}], "queries": ["x"]}
    tool = "mcp__plugin_context-mode_context-mode__ctx_batch"
    assert call(None, tool=tool, tool_input=ti) == "deny"
    assert call(None, agent_id=MAIN, tool=tool, tool_input=ti) == "ask"


def test_unrelated_tools_and_inputs_are_left_alone():
    assert call(None, tool="Read", tool_input={"file_path": "/x/acli"}) == "allow"
    assert call(None, tool="Monitor", tool_input={"ws": {"url": "wss://x"}}) == "allow"
    assert call(None, tool_input={}) == "allow"


def _run_hook(payload):
    return subprocess.run([sys.executable, str(HERE / "acli-guard.py")], input=payload,
                          capture_output=True, text=True, timeout=10)


def test_hook_prints_deny_json_with_a_reason():
    p = _run_hook(json.dumps({"tool_name": "Bash", "agent_id": "a",
                              "tool_input": {"command": "acli jira workitem assign --key TP-1 --assignee @me"}}))
    assert p.returncode == 0, p.stderr
    out = json.loads(p.stdout)["hookSpecificOutput"]
    assert out["permissionDecision"] == "deny" and "main thread" in out["permissionDecisionReason"]


def test_hook_prints_nothing_on_allow():
    p = _run_hook(json.dumps({"tool_name": "Bash", "agent_id": "a", "tool_input": {"command": "git status"}}))
    assert p.returncode == 0 and p.stdout == "", (p.returncode, p.stdout, p.stderr)


def test_unparsable_input_fails_closed_only_when_it_mentions_acli():
    p = _run_hook("not json acli jira workitem assign")
    assert json.loads(p.stdout)["hookSpecificOutput"]["permissionDecision"] == "deny"
    p = _run_hook("not json at all")
    assert p.returncode == 0 and p.stdout == ""


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    failed = 0
    for t in tests:
        try:
            t()
            print(f"PASS {t.__name__}")
        except Exception as e:  # report every failure kind, not only assertions
            failed += 1
            print(f"FAIL {t.__name__}: {type(e).__name__}: {e}")
    print(f"\n{len(tests) - failed}/{len(tests)} passed")
    sys.exit(1 if failed else 0)
