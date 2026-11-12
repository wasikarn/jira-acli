#!/usr/bin/env python3
"""acli-guard — PreToolUse hook: no acli write from a subagent, no unattended acli write.

acli on the operator's machine is logged in to a production Atlassian site. A subagent once ran
`acli jira workitem assign` on a real ticket (TP-558) although its prompt said "audit only".
This hook makes the plugin's preview-then-stop rule real:

- Inside a subagent (hook input has `agent_id`): a Bash/Monitor call whose `command` mentions
  acli is denied unless it is provably a read (`acli jira|confluence ... view|search|status|
  list*|get*`, optionally piped); a context-mode execute/batch call that mentions acli anywhere
  is denied (ctx_search, ctx_index and other non-shell context-mode tools are not checked).
- In the main thread: such a call prompts (`ask`) when what runs shows a write signal, so an
  unattended run (`claude -p`, where nobody can answer) cannot write. Not a boundary, a safety net.
- Atlassian MCP tools (a product word in the server or tool name, or an execute* tier called with
  a `name`): reads pass (get*, search*, list*, lookup*, ...; executeRead/execute with a read
  tool's name); anything else is denied in a subagent and asks in the main thread.

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
# The acli-text checks run only on tools that execute shell text; other MCP tools see branch B only.
# hooks.json matches only Bash, Monitor, these ctx tools, execute* tools and MCP names holding a
# _PRODUCT word in any case (a test pins that it skips only tools decide() allows); others are allowed.
TEXT_TOOLS = re.compile(r"^(Bash|Monitor|mcp__.*__ctx_(execute|execute_file|batch|batch_execute))$")

# Branch B: Atlassian MCP tools. Atlassian = a product word in the server part or the tool name, or
# an execute* tier called with a string `name` (the Rovo shape). Read = first verb after product words.
_MCP = re.compile(r"^mcp__(.*)__(.+)$")  # server = everything up to the LAST `__`
_PRODUCT = {"jira", "confluence", "atlassian", "bitbucket", "jsm"}
_LEAD = {"jira", "confluence", "bitbucket", "compass", "jsm", "atlassian", "conf", "bb"}
_READ_VERBS = {"get", "search", "list", "lookup", "fetch", "download", "diff", "export", "query",
               "describe", "view", "read", "find", "discover", "count", "preview"}
_READ_NAMES = {"atlassianuserinfo", "getaccessibleatlassianresources", "discover", "search", "fetch"}
_EXEC = {"execute", "executeRead", "executeWrite", "executeDestructive"}
# Input that can't be parsed or walked: block anything that may be acli or an Atlassian MCP call.
_RAW_RISK = re.compile(r"acli|atlassian|jira|confluence|bitbucket|jsm|__execute")

DENY_REASON = (
    "acli-guard: this call may write to the production Atlassian site, and subagents may only "
    "read with acli (`acli jira|confluence ... view|search|status|list*|get*`, optionally piped). "
    "Draft the command and hand it to the main thread to run after review. To read files that "
    "mention acli, use the Read or Grep tool instead of Bash. Don't move acli into a script "
    "file or build the word from pieces to get past this: that is the same write path."
)
ASK_REASON = "acli-guard: this acli call may write to the production Atlassian site. Approve only if you reviewed it."
MCP_DENY_REASON = (
    "acli-guard: this Atlassian MCP call may write to the production Atlassian site, and subagents "
    "may only call read tools (get*, search*, list*, lookup*, ... or executeRead/execute with a read "
    "tool's name). Draft the call (tool name and inputs) and hand it to the main thread."
)
MCP_ASK_REASON = "acli-guard: this Atlassian MCP call may write to the production Atlassian site. Approve only if you reviewed it."


def _words(s):
    out = []
    for part in re.split(r"[_\-]+", s):
        out += re.findall(r"[A-Z]+(?![a-z])|[A-Z]?[a-z]+|\d+", part)
    return [w.lower() for w in out]


def _mcp_is_read(name):
    if not isinstance(name, str):
        return False
    if name.lower() in _READ_NAMES:
        return True
    w = _words(name)
    while w and w[0] in _LEAD:
        w.pop(0)
    return bool(w) and w[0] in _READ_VERBS


def _atlassian_tool(tool, ti):
    """The tool's short name if it is an Atlassian MCP tool, else None."""
    m = _MCP.match(tool)
    if not m:
        return None
    server, short = m.groups()
    if "atlassian" in server.lower() or _PRODUCT & set(_words(server)):
        return short
    if short in _EXEC:
        return short if isinstance(ti, dict) and isinstance(ti.get("name"), str) else None
    return short if _PRODUCT & set(_words(short)) else None


def _branch_mcp(d):
    """allow/deny/ask for an Atlassian MCP call, or None when the tool isn't one."""
    ti = d.get("tool_input")
    short = _atlassian_tool(str(d.get("tool_name") or ""), ti)
    if short is None:
        return None
    if short in ("executeRead", "execute"):
        read = isinstance(ti, dict) and _mcp_is_read(ti.get("name"))
    else:  # executeWrite/executeDestructive land here too: "execute" is no read verb
        read = _mcp_is_read(short)
    if read:
        return "allow"
    return "deny" if d.get("agent_id") else "ask"


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
    if not isinstance(d, dict):
        return "allow"
    sub = bool(d.get("agent_id"))
    try:  # Atlassian MCP first: its writes need not mention acli at all
        mcp = _branch_mcp(d)
    except Exception:
        return "deny" if sub else "ask"
    if mcp is not None:
        return mcp
    if not TEXT_TOOLS.search(str(d.get("tool_name") or "")):
        return "allow"
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
        decision = decide(d)
    except (ValueError, RecursionError):  # unparsable, or nested past the recursion limit
        # No way to tell subagent from main thread: deny only what may be acli or Atlassian.
        d, decision = None, ("deny" if _RAW_RISK.search(raw.lower()) else "allow")
    if decision == "allow":
        return
    tool = str(d.get("tool_name") or "") if isinstance(d, dict) else ""
    mcp = tool.startswith("mcp__") and not TEXT_TOOLS.search(tool)  # only branch B blocks these
    if decision == "deny":
        reason = MCP_DENY_REASON if mcp else DENY_REASON
    else:
        reason = MCP_ASK_REASON if mcp else ASK_REASON
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": decision,
        "permissionDecisionReason": reason,
    }}))


if __name__ == "__main__":
    main()
