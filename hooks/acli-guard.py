#!/usr/bin/env python3
"""acli-guard — PreToolUse hook: no acli write from a subagent, no unattended acli write.

acli on the operator's machine is logged in to a production Atlassian site. A subagent once ran
`acli jira workitem assign` on a real ticket (TP-558) although its prompt said "audit only".
This hook makes the plugin's preview-then-stop rule real:

- Inside a subagent (hook input has `agent_id`): a Bash/Monitor call whose `command` mentions
  acli is denied unless it is provably a read (`acli jira|confluence ... view|search|status|
  list*|get*`, optionally piped); a context-mode call that mentions acli anywhere is denied.
- In the main thread: such a call prompts (`ask`) when what runs shows a write signal, so an
  unattended run (`claude -p`, where nobody can answer) cannot write. Not a boundary, a safety net.

It never parses shell to find where acli starts (that leaked about 20 ways in review). It allows
only a narrow grammar it can read exactly and treats everything else that mentions acli as a
write. Threat model: honest mistakes, not obfuscation (`ac''li`, a script file written with the
Write tool). Design, breaks and residual risks: CHANGELOG 0.1.42.

Decision table and tests: test_acli_guard.py. Output: deny/ask JSON on stdout, nothing on allow.
"""
import json
import os
import re
import shlex
import sys

# acli as a word or the last part of a path; not inside jira-acli, skills/acli/, acli-ls.py.
CAND = re.compile(r"(?<![\w.-])acli(?![\w./-])")
# The four wrappers that write (both skills ship copies under these names).
WRAP = re.compile(r"acli-(edit|new|set-desc|assign)\.sh")
VERB = re.compile(r"^[a-z][a-z0-9-]*$")
WRITE = {
    "create", "create-bulk", "edit", "transition", "assign", "delete", "clone", "archive",
    "unarchive", "restore", "update", "login", "logout", "switch", "cancel-delete", "import",
    "move", "remove", "activate", "deactivate", "visibility", "change-owner", "add-favourite",
    "reset-columns",
}
WSIG = re.compile(r"(?<![\w-])(" + "|".join(sorted(map(re.escape, WRITE), key=len, reverse=True)) + r")(?![\w-])")
# Outward-facing verbs with no WRITE word: feedback submits a report, rovodev runs an agent.
PSIG = re.compile(r"(?<![\w.-])acli\s+(feedback|rovodev)(?![\w-])")
SHELL_TOOLS = ("Bash", "Monitor")
# Same pattern as the hooks.json matcher, so a wider matcher elsewhere can't over-block Read etc.
MATCHER = re.compile(r"Bash|Monitor|mcp__.*__ctx_(execute|execute_file|batch|batch_execute)")

DENY_REASON = (
    "acli-guard: this call may write to the production Atlassian site, and subagents may only "
    "read with acli (`acli jira|confluence ... view|search|status|list*|get*`, optionally piped). "
    "Draft the command and hand it to the main thread to run after review. To read files that "
    "mention acli, use the Read or Grep tool instead of Bash. Don't move acli into a script "
    "file or build the word from pieces to get past this: that is the same write path."
)
ASK_REASON = "acli-guard: this acli call may write to the production Atlassian site. Approve only if you reviewed it."


def _strings(o):
    if isinstance(o, str):
        yield o
    elif isinstance(o, dict):
        for v in o.values():
            yield from _strings(v)
    elif isinstance(o, list):
        for v in o:
            yield from _strings(v)


def _split_pipeline(t):
    """Segments split on a lone unquoted `|`, or None if t uses anything outside the read grammar."""
    if "\n" in t or "$" in t or "`" in t:
        return None
    segs, cur, quote = [], [], None
    for i, c in enumerate(t):
        if quote == "'":
            quote = None if c == "'" else quote
        elif quote == '"':
            if c == "\\":
                return None
            quote = None if c == '"' else quote
        elif c in "'\"":
            quote = c
        elif c in ";&()<>{}#\\":
            return None
        elif c == "|":
            if t[i + 1:i + 2] in ("|", "&"):
                return None
            segs.append("".join(cur))
            cur = []
            continue
        cur.append(c)
    if quote:
        return None
    segs.append("".join(cur))
    return segs


def _read_safe(cmd):
    """True only for acli reads in the narrow grammar; cmd is already lowercased."""
    if WRAP.search(cmd):
        return False
    segs = _split_pipeline(cmd)
    if segs is None:
        return False
    for seg in segs:
        if not CAND.search(seg):
            continue
        toks = shlex.split(seg, posix=True)
        if not toks or os.path.basename(toks[0]) != "acli":
            return False
        pos = []
        for tok in toks[1:]:
            if tok.startswith("-"):
                break
            pos.append(tok)
        if not pos or pos[0] not in ("jira", "confluence"):
            return False
        verbs = [p for p in pos if VERB.match(p)]
        reads = [p for p in verbs if p in ("view", "search", "status") or p.startswith(("list", "get"))]
        if any(p in WRITE for p in verbs) or not reads:
            return False
    return True


def _write_signal(text):
    return bool(WRAP.search(text) or (CAND.search(text) and WSIG.search(text)) or PSIG.search(text))


def decide(d):
    """Return "allow", "ask" or "deny" for a PreToolUse hook input dict."""
    if not isinstance(d, dict) or not MATCHER.search(str(d.get("tool_name") or "")):
        return "allow"
    sub = bool(d.get("agent_id"))
    ti = d.get("tool_input")
    text = "\n".join(_strings(ti)).lower()
    try:
        if not CAND.search(text) and not WRAP.search(text):
            return "allow"
        cmd = ti.get("command") if isinstance(ti, dict) else None
        if d.get("tool_name") in SHELL_TOOLS and isinstance(cmd, str):
            c = cmd.lower()
            # Only `command` runs; a mention only in free text (`description`) is no call to acli.
            if not CAND.search(c) and not WRAP.search(c) or _read_safe(c):
                return "allow"
            text = c  # judge the write signal on what runs, not on the description
        if sub:
            return "deny"
        return "ask" if _write_signal(text) else "allow"
    except Exception:  # fail closed on anything that mentions acli
        if "acli" in text:
            return "deny" if sub else "ask"
        return "allow"


def main():
    raw = sys.stdin.read()
    try:
        d = json.loads(raw)
    except ValueError:
        # No way to tell subagent from main thread: deny only what mentions acli.
        d, decision = None, ("deny" if "acli" in raw.lower() else "allow")
    else:
        decision = decide(d)
    if decision == "allow":
        return
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": decision,
        "permissionDecisionReason": DENY_REASON if decision == "deny" else ASK_REASON,
    }}))


if __name__ == "__main__":
    main()
