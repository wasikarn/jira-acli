# Changelog

All notable changes to `jira-acli` are documented here. Format loosely follows
[Keep a Changelog](https://keepachangelog.com/); versions follow [SemVer](https://semver.org/).

Pre-`1.0.0`: breaking changes may land in any `0.x` release.

This file starts at `0.1.18` — releases before that predate the changelog. See
`git log` for the full history back to `0.1.0`.

## [0.1.47] — 2026-11-12
From the `mh:deep-audit` recheck of 0.1.46 and its whole-picture challenge (`mh:blind-spot-hunter`),
both on Claude.
- **Deeply nested input no longer crashes the guard.** A tool input nested past Python's
  recursion limit raised `RecursionError`. Under `onFailure: block` that blocked the call: a
  context-mode call on any Python, and any MCP call on macOS's `/usr/bin/python3` 3.9. Now it is
  judged like unparsable input: denied when it mentions acli, allowed otherwise.
- **Tests:** the MCP reason test now compares each reason exactly. 0.1.46's substring check still
  passed when a main-thread ask showed the subagent deny text. A new test reads `hooks.json`: the
  timeout is above 5 s, `onFailure` is block, and the matcher reaches every tool the corpus
  guards but not `Read` or `TodoWrite`.
- **Docs:** the context-mode rule covers only the execute and batch tools (`ctx_search` and
  `ctx_index` are not checked). README and the docstring said "any context-mode call".

## [0.1.46] — 2026-11-12
Fixes from `mh:deep-audit` on 0.1.45 (checker on Claude; Codex was over quota). The guard's
logic is unchanged.
- **`hooks.json`:** the description now names Atlassian MCP writes, and the timeout is 10 s, the
  same as the user-level entry. A verbatim copy of the old 5 s failed the dotfiles fail-closed
  check, which wants more than 5 s for a guard with no deadline of its own.
- **Test:** the main-thread MCP `ask` now has its reason checked too. Before, the suite still
  passed with every `ask` using the acli reason.
- **Correction to 0.1.45:** the accepted over-blocks also include a non-Atlassian server's
  `execute`/`executeRead`/`executeWrite`/`executeDestructive` called with a string `name`. The
  guard treats it as Atlassian, so it is denied in a subagent and asks in the main thread.

## [0.1.45] — 2026-11-12
**New: the guard covers Atlassian MCP tools.** Once the official Atlassian plugin is installed,
its MCP tools create and edit issues directly, and `general-purpose` subagents inherit them.
Designed with `mh:attack-proposal` (3 attack lanes, 28 breaks; validator rounds 3 of 3, all on
Claude because Codex was over quota). Round 3 still found 2 breaks, so the verdict was NO-GO;
the operator chose to build rev 4 with the one-word fix below and accept the other as residual.
- **Which tools:** an MCP tool is Atlassian when a word of its server name or tool name is
  jira, confluence, atlassian, bitbucket or jsm, or it is `execute`/`executeRead`/
  `executeWrite`/`executeDestructive` called with a string `name` (the Rovo call shape). This
  covers the official plugin, a claude.ai connector, a server named `atlassian`, and third-party
  servers keyed `jira`/`confluence`/`bitbucket`.
- **Reads pass:** the first verb of the name, after product words such as `jira`, `conf` or
  `bb`, is get, search, list, lookup, fetch, download, diff, export, query, describe, view, read,
  find, discover, count or preview; or the tool is atlassianUserInfo,
  getAccessibleAtlassianResources, discover, search or fetch. `executeRead`/`execute` pass only
  when the tool named inside is a read.
- **Everything else** is denied in a subagent and asks in the main thread, with its own reason
  text. The plugin's documented MCP reads (`getJiraIssue`, `executeRead` lookups) pass; its
  documented writes (jira-content and confluence-content Step 5) ask once after the chat go-ahead.
- **Wiring:** `hooks.json` now matches `^(Bash|Monitor|mcp__.*)$` (anchored, so `TodoWrite` and
  the like never match). Non-Atlassian MCP tools pass untouched; the acli-text checks still run
  only on Bash, Monitor and the context-mode shell tools.
- **Residual risks:** a server named without any product word exposes Goals, Projects, Teams,
  Focus, Talent, capacity-planning, Compass, Teamwork Graph, Loom and Assets writes; an MCP
  gateway that runs any tool by name (Docker MCP Toolkit's `mcp-exec`) is a generic proxy the
  guard can't see through. Accepted over-blocks: reads whose first verb isn't on the list
  (`resolveConfluenceContentMacros`, `scanCodeRepo`), and `executeRead` with no `name`.
- **Not built: the script detour.** Two designs (checking script files at write time, then the
  files a command runs) leaked through shell parsing in attack and were dropped. A subagent
  that writes acli into a script and runs it is still not checked; the deny reason (0.1.44)
  tells it not to.
- **Tests:** `hooks/testdata/mcp.json` (412 rows from the validator, sub and main) and a
  fail-closed test for a crash in the MCP check. 12 of 12 branch mutants fail the suite. Removed
  as dead code: the script's `MATCHER` gate and a redundant `executeWrite` branch.

## [0.1.44] — 2026-11-12
Fixes from the second `mh:deep-audit` pass on the guard: a recheck of 0.1.43 and a
whole-picture challenge (`mh:blind-spot-hunter`), both on Claude.
- **The main-thread write check now reads only `command`.** A read whose description held a
  WRITE word ("Search issues to update later") asked, so `claude -p` could not run it. Any write
  verb is still in `command`, so this never lets a write past.
- **The deny reason warns against the script detour:** moving acli into a script file or
  building the word from pieces is the same write path. The hook still can't see inside a script
  the Write tool made (0.1.42 residual risk); the message lowers the odds that an honest agent
  tries it.
- **Test fix:** the Monitor description row never exercised 0.1.43's fix (its command passed
  before it). It now carries `2>&1`. 27 of 29 mutants fail the suite (one new mutant for the
  main-thread change); the same two equivalent survivors as 0.1.43.
- **Checked, no change needed:** all 95 leaf commands of acli 1.3.40-stable, walked through
  `--help` (local, no API call) and run through the guard. The 30 allowed in a subagent are all
  reads; every write leaf is denied in a subagent and asks in the main thread, except
  `config gov-cloud` (known residual). With one PreToolUse hook answering `allow` and another
  `ask`, Claude Code blocked the call in `claude -p` (probe), so another tool's hook can't
  cancel the guard's `ask`.
- README, `jira-expert` and the script's docstring now state the narrower rule: Bash/Monitor
  reads in the plain shapes pass, ctx tools that mention acli are denied.

## [0.1.43] — 2026-11-12
Fixes from `mh:deep-audit` on the 0.1.42 guard. Its checker ran on Claude (Codex was over quota),
so independence was reduced.
- **An acli mention only in `description` no longer blocks a call.** 0.1.42 counted every string
  in a Bash or Monitor call, so a subagent's `cd /tmp && ls` described as "List acli plugin
  files" was denied, against the design's own rule (only `command` runs). The guard now allows
  a Bash/Monitor call whose `command` names neither acli nor a write wrapper. A write is always in
  `command`, so no call denied for its command is allowed now.
- **Correction to 0.1.42:** the context-mode tools (`ctx_execute`, `ctx_execute_file`,
  `ctx_batch`, `ctx_batch_execute`) have no read grammar. In a subagent any acli mention in them
  is denied, a plain `view` and the `intent` text included; 0.1.42 wrongly listed them under
  "denied unless provably a read".
- **Main thread, accepted and now tested:** acli plus a WRITE word anywhere in one command asks,
  commit messages included (`git commit -m "fix: acli edit wiped the body"`), so an unattended
  run can't make that commit. Reword it or commit interactively.
- **Tests: 0.1.42's "11 of 11 mutations" was too narrow a set.** The checker's 26 mutants left 9
  alive, one of them a guard with no pipe split that allowed `acli ... view | acli ... assign`.
  New rows: a read piped into a write, a read piped into `xargs acli ... assign`, a read and a
  write verb in one command, `||`, `\` inside double quotes, `#`, an absolute-path read and a
  non-acli program; new tests for a description-only mention and the fail-closed `except` path.
  26 of 28 mutants now fail the suite. The two left are equivalent: without the unterminated-quote
  check `shlex` raises and the `except` path denies anyway, and without the Bash/Monitor tool
  check no ctx tool sends a `command` key. Corpus: 96 single-line rows, 7 multi-line inputs, 16
  tool calls.
- A user-level copy of the script (see 0.1.42) must get the same change.

## [0.1.42] — 2026-11-12
**New: `hooks/acli-guard.py`, a PreToolUse hook that blocks acli writes from subagents.** 0.1.41
only reworded the README: `jira-expert` and `confluence-expert` keep `Bash` for read-only acli,
so nothing stopped a write, and a dispatched subagent once left TP-558 unassigned this way.
Designed with `mh:attack-proposal` (2 attack lanes, 24 breaks; validator passed in round 3 of 3;
both lanes and the validator ran on Claude, Codex was over quota, so independence was reduced).
- **Subagents** (hook input has `agent_id`): any Bash, Monitor or context-mode `ctx_execute`/
  `ctx_batch` call that mentions acli is denied unless it is provably a read:
  `acli jira|confluence ... view|search|status|list*|get*`, optionally piped, with no `$`,
  backtick, newline, `;`, `&`, `( ) < > { } #` or `\` outside quotes, and none of the four write
  wrappers (`acli-edit.sh`, `acli-new.sh`, `acli-set-desc.sh`, `acli-assign.sh`).
- **Main thread**: a call that mentions acli and shows a write signal (a WRITE verb word, a
  wrapper `.sh`, `acli feedback|rovodev`) gets `ask`. Verified: an `ask` blocks the call in an
  unattended `claude -p` run under `bypassPermissions`. A safety net, not a boundary.
- It does not parse shell to find where acli starts; a parser leaked about 20 ways in review.
  Accepted over-blocks in subagents: `acli ... --help` and `--generate-json`, redirects,
  `cd x && acli ...`, `$VAR`, heredocs and multi-line commands that mention acli, `git`/`grep`
  on a wrapper `.sh` path, commit messages with the word acli. The deny reason points the agent
  to the main thread, or to Read/Grep for files.
- Residual risks: obfuscated forms that never spell `acli` (`ac''li`, `${A}i`, a script written
  with the Write tool), Codex/Orca workers whose shells skip Claude Code hooks, and main-thread
  acli calls with no write word (`acli config gov-cloud`).
- The hook runs only while the plugin is enabled (`defaultEnabled: false` keeps it off until
  then, verified with `--plugin-dir`). Register the same script as a user-level PreToolUse hook
  to cover every session.
- Tests: `hooks/test_acli_guard.py` runs the validated corpus (88 single-line rows, 7 multi-line
  inputs, 11 tool calls) plus main-thread cases. 11 of 11 mutations of the guard's rules fail it.
  End to end through a real Claude Code session with a stub acli: a subagent's `view` ran, its
  `assign` was denied; a main-thread `assign` was blocked by the `ask`; `jira-expert` on a read
  task ran 3 acli reads with no denial and got `${CLAUDE_SKILL_DIR}` already filled in.
- README, CLAUDE.md and both agents now describe the hook.

## [0.1.41] — 2026-11-12
Fixes from a whole-project `mattpocock-skills:code-review` (Standards and Spec axes).
- **`acli-edit.py` could wipe a description.** A view payload for another issue, or a dict with
  no `fields` object, became an empty doc, so append mode sent only the new text and the edit
  replaced the whole body. It now fails with `FATAL:` and writes no payload. Key matching
  ignores case (`tp-1` matches `TP-1`), and a bare ADF doc is used as the current description,
  as the offline testing aid in `jira-content` documents (before, append dropped it and kept only
  the new text). New `test_acli_edit.py` pins all of this.
- `acli-new.sh` exits non-zero with `FATAL:` when a create returns no key, and says to search
  before retrying, instead of printing `(no key returned)` and exiting 0.
- `print-edit-result.py` and `inject-mermaid-macros.py` fail with `FATAL:` on bad or unexpected
  JSON instead of a traceback or an unprefixed message.
- `--dry-run` now works in any argument position for all four write wrappers, through a shared
  `_dry-run.sh`. Before, `acli-assign.sh` and `acli-set-desc.sh` read it only as the third
  argument. `acli-set-desc.sh` and `acli-ls.sh` resolve their directory with `BASH_SOURCE[0]`.
- `adf-node-diff.py` reuses `adf2md.py`'s new `read_json` instead of its own copy.
- `confluence-expert`'s stop rule now covers `space update|archive|restore` and any other acli
  command that changes state, not only `blog create` and `space create`.
- README and CLAUDE.md no longer claim the agents can't fire acli; they keep `Bash`, so the rule
  is an instruction. CLAUDE.md lists the `test_*.py` scripts and every shipped script, and
  describes what `adf2md.py` accepts. A dead `run-tests.sh` pointer in `md2adf.py` is gone.

## [0.1.40] — 2026-11-12
- The read-back also skips a field the user agreed to leave out after a rejected create (the
  0.1.38 `versions` rule asks for that OK after the preview, which 0.1.39's skip didn't cover).
- 0.1.39's entry said Step 3 has the ask-first assignee rule; that rule is in Failure Modes, and
  Step 3 only names the project default. Wording corrected.

## [0.1.39] — 2026-11-12
Fixes from a fresh checker on 0.1.37–0.1.38 (Claude fallback, Codex usage limit).
- Corrects 0.1.38's assignee line: a ticket created without an assignee gets the project's
  default assignee, which can be the project lead, so the preview no longer promises
  "unassigned". An assignee that can't be resolved is now asked about first. Step 3 now names the
  project default.
- The read-back skips a field the user agreed at the preview to leave out (a version or assignee
  dropped with their OK), instead of stopping on a ticket that matches what they approved.
- A Sub-task rejected for an invalid parent now stops and asks, instead of retrying with a parent
  the user never confirmed.
- 0.1.37's "compare by meaning" rule (commit `ee9d8ab`) was pushed under the same version number
  without a changelog line; it is recorded under 0.1.37 now.

## [0.1.38] — 2026-11-12
- `jira-content` Failure Modes: a Bug create rejected for an unknown `versions` value now stops and
  asks, instead of retrying without the version. The user confirmed a preview that had it, and the
  repo's **Fail loud** rule says never drop and retry.
- An assignee that can't be resolved is left unassigned and named in the preview, since assignee is
  not on the rendered card.

## [0.1.37] — 2026-11-12
Corrects 0.1.36 and finishes 0.1.30, from `mh:deep-audit` on 0.1.30–0.1.36 (checker ran on
the Claude fallback, Codex usage limit). 0.1.36's read-back used `acli jira workitem view`, but
Step 5b also runs when acli is unavailable or logged out, so in two of its three trigger cases
the required check could not run. It now reads with MCP `getJiraIssue` (Primary on v2) and
sorts each field into set / empty / absent from the response. Only "set" counts as a clean
create, and an absent field is cross-checked with acli when logged in, else the user is asked
to check the ticket. acli's view is not trusted for `labels` (`acli/ISSUES.md` Issue 3). The
0.1.30 fix for `--ignore-errors` missed `skills/acli/SKILL.md:57` (also still said
`1.3.22-stable`) and `skills/acli/ISSUES.md:187`; both now say an invalid transition fails
loud unless you pass `--ignore-errors`.

A whole-picture pass on those fixes found more gaps, also fixed here:
- A dropped `priority` or `assignee` comes back as the project default, not empty, so the
  read-back now treats "present but a different value" like empty. It covers fields the
  user stated, not only the ones sent. `description` is checked for presence only (its stored
  form can differ from the Markdown sent); the user is asked to look at the rendered ticket once.
- `jira-expert` holds no MCP tools, so its handoff of an MCP create or edit must list the
  `getJiraIssue` read-back as the step after the fire. Otherwise the main thread may fire
  without `jira-content` loaded.
- `skills/acli/SKILL.md` now asks for the same read-back after `editJiraIssue`, which can drop
  fields the same way.
- The acli cross-check must read the same site the MCP create wrote to.
- Failure Modes: omitting a not-found `versions` now names it in the reply.
- "Set" compares by meaning, not literal text: the response may wrap a value
  (`{"name": "High"}` for `priority`) or return `environment` as rich text in another form.
- `confluence-content` no longer calls the `acli/SKILL.md` section the "full" v2 contract.
  Atlassian's `getConfluenceSpace` space-instructions step is not adopted.

## [0.1.36] — 2026-11-12
`jira-content` Step 5b now requires reading the ticket back after every MCP create
(`acli jira workitem view <KEY> --fields '*all' --json`) and checking each field that was sent.
On v2 a wrong parameter name can be dropped with no error, and the v2 names for
`environment` and `versions` (Affects Version) are not confirmed, so a Bug could land on
production with those fields empty. If any field is empty, the reply names it and stops; no
retry with guessed names. A read-only MCP test cannot catch this; only the first real
create can.

## [0.1.35] — 2026-11-12
Corrects 0.1.31–0.1.34. Those releases put v2 tool names on v1 call shapes. Atlassian's v2
skills show different parameters for create, read and update (plus a required
`snapshotToken`) and say an `execute` call drops unknown parameters without an error, so the
create, edit and mermaid flows would likely have failed or lost values on v2. Call shapes now follow Atlassian's own v2 skills in
`atlassian/atlassian-mcp-server` at `b74220d` (the commit the official plugin pins), with
v1 shapes kept beside them:
- deferred tools run as `executeRead(name, cloudId, inputs)`; `discover` when the name or
  inputs are unknown;
- `lookupJiraAccountId` takes `query` (not `searchString`);
- `createJiraIssue` takes `issueType`, `assignee` and a top-level `priority`;
- Confluence reads need `detail="full"`, updates need the read's `snapshotToken`, and
  create/update take `body={"format", "value"}`, plus `parent` and `contentType` on create.

The mermaid and macro-page ADF flows are marked "not yet run on v2": Atlassian's examples
show only `"markdown"`, so the docs say to confirm `"adf"` in the live schema first and to
stop rather than fall back to markdown. Still not shown in those examples:
`listJiraIssueTransitions` inputs, `editJiraIssue` fields, and the v2 response shapes. No
live v2 call was made.

## [0.1.34] — 2026-11-12
Fixes from `mh:deep-audit` on 0.1.31–0.1.33 (checker ran on the Claude fallback, Codex
usage limit). The official Atlassian plugin pins `https://mcp.atlassian.com/v2/mcp`, so
`skills/acli/SKILL.md` now says `discover` + `executeRead` is the only path for plugin
users and scopes `?tools=all` to a self-configured server (which loses the
`mcp__plugin_atlassian_atlassian__` prefix). `skills/acli/ISSUES.md` no longer implies the
TP-884 check covered the v2 route. `confluence-content` no longer says
`updateConfluenceContent` *always* replaces the whole body: v2 lists "granular edits",
not verified here, and granular edits stay off until checked (the macro-safety steps assume
a full-body replace). Tests run on v1 tools (the html-vs-adf write test on a scratch page,
the TP-807 macro wipe, the large-body write) now say so. `executeWrite`/`executeDestructive` need the same preview-and-confirm as
acli writes; the v1 cutoff date cites Atlassian's upgrade page; response shapes join the
"not verified on v2" caveat. The 0.1.31–0.1.33 entries below were reworded where they claimed
more than the files hold.

## [0.1.33] — 2026-11-12
Found by `mh:attack-proposal` on the 0.1.32 dual-name change: on Atlassian's default
v2 endpoint only `Primary` tools are listed to the agent, and six tools the docs name
(`listJiraIssueTransitions`, `listJiraProjects`, `listJiraProjectIssueTypesMetadata`,
`getJiraIssueTypeMetaWithFields`, `lookupJiraAccountId`, `listConfluenceSpaces`) are
deferred, so an agent told to call them directly would not find them. `skills/acli/SKILL.md`
now explains the path (discovery tool, then `executeRead`, or the `?tools=all` endpoint);
call sites outside that section carry a one-clause pointer or link to it. Attacker ran on the Claude
fallback (Codex usage limit), so independence is reduced. Not yet checked: whether
`executeRead` takes a bare tool name without a prior discovery call.

## [0.1.32] — 2026-11-12
The first mention of each renamed v2 tool in each skill, agent and `inject-mermaid-macros.py`
file, plus every `mcp__plugin_atlassian_atlassian__`-prefixed call, carries its v1 name beside
it (`createConfluenceContent` (v1: `createConfluencePage`)); later mentions in the same file
may use the v2 name alone. `skills/acli/SKILL.md` holds the full v1→v2 list.
Also renamed the `mcp__plugin_atlassian_atlassian__`-prefixed v1 names that 0.1.31 missed
(`createConfluencePage`, `updateConfluencePage`, `getConfluencePage`, `getVisibleJiraProjects`,
`getJiraProjectIssueTypesMetadata`, `getConfluenceSpaces`). v2 parameter shapes still unverified.

## [0.1.31] — 2026-11-12
Atlassian MCP tool names moved from v1 to v2 across the skills and agents:
`createConfluencePage`/`updateConfluencePage`/`getConfluencePage` →
`createConfluenceContent`/`updateConfluenceContent`/`getConfluenceContent`,
`getTransitionsForJiraIssue` → `listJiraIssueTransitions`, and three `get*` →
`list*` renames. `skills/acli/SKILL.md` carries the v1→v2 list. v1 stays live
until 2027-03-01. Parameter shapes (`cloudId`, `contentFormat`) are NOT
verified against v2; names come from Atlassian's supported-tools page only.

## [0.1.30] — 2026-11-12
Reference refresh against acli `1.3.40-stable` (was `1.3.22-stable`); docs only.
Crawled the full `--help` tree and diffed it against `skills/acli/REFERENCE.md` +
`references/REFERENCE-detail.md`: workitem flag tables already matched. Fixed
the rest: `acli completion` removed, `acli guard` added, global `auth login` has
no `--web` (per-product logins do), `confluence page view` gained six
`--include-*` flags, `transition` accepts `--ignore-errors` (docs said it
didn't), and the board/filter/field/admin/watcher subcommand lists were
completed. Behavioral claims (30-row cap, `space list --keys`) were not
re-run: acli was unauthenticated.

## [0.1.29] — 2026-09-03

Prompt-cleanup pass, no behavior change.

`skills/jira-content/SKILL.md`: trimmed the frontmatter `description` +
`when_to_use` from ~1,468 to 1,289 characters — same triggers, exclusions,
and foreign-skill guard, just fewer words — restoring headroom under Claude
Code's 1,536-character cap so the next routing tweak doesn't silently get
truncated out of the skill listing.

`agents/jira-expert.md`, `agents/confluence-expert.md`: rewrote four dated
"Confirmed gap (2026-08-04)" narrative paragraphs as present-tense rules.
The reasons behind each rule are kept; the incident-report framing (what
was tried, when, what happened) is gone, since an agent reading the file
needs the rule, not the history.

## [0.1.28] — 2026-08-21

`CLAUDE.md`: fixed a doc-drift regression introduced by 0.1.27's own change —
adding `SCRIPT_DIR`/`print-edit-result.py` to `acli-assign.sh` silently broke
the Architecture section's claim that the script "needs neither [path
resolution]; it calls no sibling script." Corrected the wrapper count (4 of 5
→ all 5) and folded `acli-assign.sh` into the `BASH_SOURCE[0]` group. Found
via a deep-audit pass re-verifying 0.1.27's changes against the live files
instead of trusting the prior summary.

## [0.1.27] — 2026-08-21

8 commits landed since 0.1.26 without a version/changelog update; this entry
catches all of them up.

`adf2md.py` (the ADF→Markdown reader): fixed four independent rendering bugs
found via parallel fan-out review and drill-down verification against
Atlassian's official ADF docs — `render_card()` crashed with a raw
`AttributeError` instead of exiting cleanly when `fields.description` was a
plain string rather than ADF; the `subsup` mark (superscript/subscript)
wasn't rendered at all, silently dropping the styling; `orderedList.attrs.order`
was ignored, so a list resuming after an interrupting paragraph/image always
renumbered from 1; and `render_table` didn't pad ragged body rows to the
header's column count the way `md2adf.py`'s write side already did, producing
a misaligned Markdown table. All four verified with minimal repros; all
regression suites still passed.

`acli-edit.py`: `--remove-section`/`--replace-section` heading matching only
read `"text"`-type inline nodes, so a heading built via Jira's emoji picker
(e.g. "🎯 Goals") could never be matched even when the user typed the exact
displayed text — now also pulls text from emoji/mention/status nodes.

Docs: corrected three verified inaccuracies found via drill-down/live
verification — `confluence space list --keys` doesn't actually filter (still
returns the full unfiltered list; the prior Issue 8 fix's own workaround
silently resolved the wrong space), `acli jira project view` requires
`--key` as an explicit flag rather than a bare positional, and CLAUDE.md's
Architecture section overstated `confluence-content`'s MCP dependency (reads
go through `acli confluence page view` first) and the path-resolution
convention (2 of 5 `.sh` wrappers use `dirname "$0"`, not `BASH_SOURCE[0]`).

`acli-new.sh`/`acli-assign.sh`: found via a full-repo Standards audit of
every tracked `.sh`/`.py` script — neither previewed its payload before
firing, unlike `acli-set-desc.sh`; both now support `--dry-run`.
`acli-new.sh`'s bare-doc guard also collided the ADF node-type key with the
Jira issue-type key (a custom issue type literally named "doc" would have
false-positived); now checks for `"summary"` instead. `md2adf.py` gained
write support for `<u>`/`<sup>`/`<sub>` so underline/subsup marks round-trip
with `adf2md.py` instead of silently dropping on rewrite (mark shapes
verified against Atlassian's official ADF docs). Also deduped two repeated
logic blocks: a result-parsing one-liner shared by
`acli-assign.sh`/`acli-edit.sh` (now `print-edit-result.py`), and
`acli-edit.py`'s heading-text extraction (now imports `adf2md.py`'s
`plain_inline_text` instead of re-deriving it). `inject-mermaid-macros.py`'s
7 site-identity flags are now bundled into a `SiteConfig` dataclass instead
of being threaded individually.

## [0.1.26] — 2026-08-04

`jira-expert` (agent): closed the asymmetry flagged as un-actioned in 0.1.25 — does
`jira-expert.md`'s Hard Rule 4 ("Never touch Confluence") have the same read-only-lookup gap
`confluence-expert.md`'s Hard Rule 4 had before its 0.1.25 fix? A purpose-built eval (real TP-807,
its 10 real sub-tasks, its linked Confluence spec page id 217743376) confirmed yes, plus a second,
unrelated gap. Iteration 1's 2-reviewer review found two double-confirmed major findings: (1) Hard
Rule 4 gap — with_agent correctly deferred all Confluence access but couldn't answer the user's
direct "is the spec finalized?" question at all, forcing a needless second-agent round-trip;
reviewers split on severity (minor vs major) and on fix shape (a narrow metadata-only carve-out vs
a target-bounded, attribution-required one) — the user chose the latter (reviewer 2's design) via
an explicit gate. (2) JQL-thoroughness gap, unrelated to Confluence — with_agent never ran
`parent = TP-807` (pure Jira, zero Confluence involvement) and as a result falsely claimed "no
visibility into implementation progress," missing all 10 real sub-tasks (2 unstarted); this fix
landed in the "Read/search/triage" guidance, not Hard Rule 4. Iteration 2's fix closed both,
re-verified live by 2 independent reviewers: `parent = TP-807` now runs and correctly surfaces the
2 unstarted sub-tasks; the Confluence carve-out held to all four of its bounds (one call, one
page, no traversal, attribution with version/date surviving into the actual drafted comment
payload, no contradiction-scanning) and the run now answers the user's original question via
attribution instead of punting it. Verdict: **improved** (0 critical/2 major → 0 critical/0
major), a clean result unlike 0.1.25's flat verdict. One new double-confirmed minor surfaced: the
carve-out's "a single read-only lookup" wording is a call-count bound, not a mechanism pin, so
with_agent went to the Atlassian MCP instead of acli's own `confluence page view
--include-version` (the doctrinally-correct default per `skills/acli/SKILL.md`) — self-disclosed,
zero factual harm, and confirmed unreachable in real deployment: `jira-expert.md`'s own Hard Rule
3 ("You hold no MCP tools") already forecloses the MCP path independently of Hard Rule 4's
mechanism silence, and the actual frontmatter grant (`Read, Grep, Glob, Bash`) confirms it —
logged as un-actioned, matching this file's own "flag, don't silently ship" pattern. A second new
finding (with_agent's volunteered "correction" about the Confluence space key was itself wrong —
BEP is the real key, the task brief was right) was double-confirmed but not tallied: it's a
general model-accuracy slip (inferring a canonical identifier from a URL path) rather than
anything Hard Rule 4 governs, though it arguably falls under Hard Rule 1's existing
under-verified-secondary-claims addendum — noted for a future pass rather than folded into this
one.

## [0.1.25] — 2026-08-04

`confluence-expert` (agent): first-ever fixture-eval + `kbg:review-fixtures` + `kbg:iterate-skill`
loop against this agent (no prior workspace existed). 3 evals × with_agent/baseline, grounded in
live production data on `100-stars.atlassian.net`: a real Confluence page (TP-807 Spec, id
`217743376`, independently confirmed to carry 7 `expand` + 7 `extension` macro nodes — the exact
page that lost all 7 diagram macros to a markdown-format full-body-replace in a real 2026-07-14
incident already documented in `confluence-content/SKILL.md`), a confirmed-nonexistent "incident
log" page in space BEP, and the real TP-826 ticket (also used in the `jira-expert` round earlier
this session). Iteration 1's review found 0 critical/major findings and exactly 1 double-confirmed
minor: `agents/confluence-expert.md`'s Hard Rule 4 ("Never touch Jira work items") has no read-only
carve-out, so a run correctly deferred a Jira transition but declined even a one-line status check
first — current behavior wasn't wrong under the existing wording, but the check would have
improved the handoff at no real cost. The round's one genuine technical bug — a baseline run
recommending `contentFormat: "storage"` for the real `updateConfluencePage` MCP tool, which only
accepts `html`/`markdown`/`adf` (independently verified against the live tool schema by both
reviewers) — traced to the *baseline*, not the target, confirming `confluence-expert`'s specialized
MCP-format knowledge has real, measurable value. Iteration 2's fix (one sentence added to Hard Rule
4 permitting a single read-only lookup to confirm a handoff fact, with explicit limits on what it
may not be used for) closed the finding precisely — re-verified live: the regenerated run performed
exactly one `workitem view` call, explicitly stated it stopped there, and both reviewers confirmed
the reported facts matched production exactly. No regressions in the other 2 evals. One new,
double-confirmed-but-non-harmful minor finding surfaced during the iteration-2 Verify pass — the
new sentence's "a fact you're about to hand off" wording is ambiguous between "handoff to
jira-expert" and "fact used in my own draft," and a regenerated run reached for the broader reading
once; both reviewers independently confirmed this caused no actual over-reach (call stayed scoped,
no legality judgment, no recommendation formed) and was mechanically justified regardless (the
paginated search result genuinely truncated the relevant ticket's summary). The mechanical tally is
therefore flat (1 minor → 1 minor) rather than "improved," but the original finding is verifiably
closed and the replacement finding caused zero demonstrated harm — the user chose to stop at
iteration 2 (of a 3-iteration cap) rather than chase a non-harmful wording nit, and logged a
second, single-sourced follow-up (the rule doesn't specify which command satisfies "one lookup";
observed instrument choice varied between a full `workitem view` and a narrower `search --fields`)
as un-actioned for a future pass. **Flagged, not actioned:** this leaves the product-boundary
rules asymmetric — `jira-expert.md`'s mirror rule ("Never touch Confluence. Defer to
`confluence-expert`...") has no matching read-only carve-out. No fixture evidence exists that
`jira-expert` actually hits this gap, so it wasn't speculatively patched (Rule 2); a future
fixture round against `jira-expert` should check for it before mirroring the sentence.

## [0.1.24] — 2026-08-04

`jira-expert` (agent): closed 1 real defect found via a fixture-eval + `kbg:review-fixtures`
+ `kbg:iterate-skill` loop against this repo's first Agent target (3 evals × with_agent/
baseline, 2 iterations, 2 independent reviewers per round — the loop stopped at iteration 2
by user choice, under the 3-iteration cap). Iteration 1's review found with_agent's ad hoc
label-vocabulary check during Bug drafting used a bare `--json` call over a broad query,
silently capped at 30 of 519 real matches, and concluded a label (`notification`) didn't
exist when it actually did (in use on TP-1003 and TP-777) — inventing `push-notification`
as a new label instead of reusing existing vocabulary. This is the same nested-search-under-
a-different-primary-task failure mode already fixed once in `confluence-content` (0.1.23),
now independently reproduced a third time this session, this time inside `jira-expert`'s own
ad hoc verification searches rather than a stated search task. A second, minor finding in the
same round: with_agent's rendered Bug preview listed a "simpler" acli create option first even
though its own transcript called that option "not recommended," risking a user picking the
option that silently drops a field they'd explicitly stated. Iteration 2's fix (a completeness
caveat added to Hard Rule 1 — ad hoc verification searches are subject to the same
`--count`/`--paginate` discipline as a stated search task; an option-ordering rule added to
the Output section — order/label multiple drafted paths by actual recommendation, not
simplicity) closed both, independently re-verified live by both reviewers against production
Jira (exact label counts, ticket keys, and search counts all reproduced). No regressions in
the other 2 evals; no over-correction (read-only tool-call counts held flat or dropped).
Per the loop's iteration cap (3), and since both target findings closed clean on the first
re-verification, the user chose to stop at iteration 2 rather than continue. One new,
single-sourced finding surfaced during the iteration-2 Verify pass — with_agent's duplicate-
precedent search is Latin-script-only in a project where most summaries are Thai, missing a
real related ticket (TP-777) that its own label check found by a different path — logged as a
new, un-actioned follow-up for a future pass, not folded into this release. This session also
uncovered and documented a standing methodology caveat for any future fixture round in this
repo: this project's own `CLAUDE.md` auto-imports `acli/SKILL.md` in full, so a "baseline" (no
target skill/agent read) still carries acli's own mechanical knowledge — any eval aimed at
discriminating on acli-level knowledge alone will not discriminate in this repo's environment.

## [0.1.23] — 2026-08-04

`confluence-content`: closed the un-actioned follow-up finding logged in 0.1.22 — a JQL search
undercount (an `acli --json` result reported "30 hits," true count 395) in the Step 1
Jira-cross-check step. Investigated first as a possible `acli` fix: re-tested the same class of
gap directly against `acli`, once with 2 new fixture evals (a primary-task count query and a
bulk-mutation preview, both grounded in real live counts on project TP) and cross-checked
against an earlier, already-completed 3-iteration `acli` fixture round from earlier this session
that had independently tested the identical pagination-cap trap (`eval-pagination-search`). Both
rounds agree: `acli`'s existing `--count`/`--paginate` warning is reliably applied whenever a
Jira search is the agent's stated primary task — 100% pass rate across all runs in both rounds,
with or without the skill invoked. The real miss only reproduces when a Jira search is a
secondary, incidental step nested inside a larger, different-domain task (drafting a Confluence
page) — an attention-competition failure, not a missing-warning failure, and not something an
edit to `acli`'s own text would reach. Fix applied at the actual locus instead:
`confluence-content`'s Step 1 paragraph now explicitly names this failure mode and repeats the
`--count`/`--paginate` cross-check instruction at the point where the search result is about to
be trusted, rather than relying on the warning living only in a different skill's file.
`jira-content` was checked for the same nested-search pattern and doesn't have one — it doesn't
search Jira for grounding facts before authoring content, so no equivalent fix was needed there.
This one wasn't run through the full fixture-eval + review-fixtures + iterate-skill loop — the
diagnosis (two independent non-discriminating rounds) already located the fix precisely enough
that a live re-test would mostly re-confirm the diagnosis rather than surface anything new;
worth a lighter-weight verification pass in a future session if this area gets touched again.

## [0.1.22] — 2026-08-04

`confluence-content`: closed 3 real defects found via a fixture-eval + `kbg:review-fixtures`
+ `kbg:iterate-skill` loop (3 evals × with/without skill, 3 iterations, 2 independent
reviewers per round). Iteration 1's review found 2 MAJORs and 1 MINOR: the "editing an
existing page" procedure never re-checked the page's version immediately before firing a
write, only at the initial read; drafting a new Spec's Requirements/AC never cross-checked
Jira, so a fixture run assumed continuous spend tracking for a system that actually
processes spend in discrete booking increments; and the Mermaid-embed procedure had no
Failure Modes guidance for a mid-sequence failure. Iteration 1's fix (a version-recheck
step 2.5 before the write; a Step 1 Jira-cross-check paragraph for new Specs; 2 new Failure
Modes bullets) closed all three, confirmed by two more independent reviewers — one of whom
independently re-tested the injector's idempotency claim by running it twice and diffing
the output — but surfaced a new MAJOR: the Jira-cross-check paragraph's "for a new Spec"
wording let a sibling eval (documenting an existing webhook-retry flow, not a "new Spec")
reason its way past the rule and invent every retry-policy number, recreating the original
failure through a scoping loophole. Iteration 2's fix (widened the rule's scope to any page
asserting specific system-behavior facts, and explicitly foreclosed the "this isn't really
a Spec" rationalization) was independently re-verified by both reviewers via live Jira
reads (TP-834, TP-826, TP-140) confirming the research is load-bearing — concrete AC lines,
diagram steps, and a "no DLQ" domain fact all trace directly to real tickets, not decorative
citation. Per the loop's iteration cap (3), this fix session stops here. The same final
round surfaced one new, unrelated finding: a spec-page-draft fixture accepted an
`acli --json` search result reporting "30 hits" without a `--paginate`/`--count`
cross-check — the real count was 395 (a >13x undercount, matching the exact silent-cap trap
`acli/SKILL.md` already documents elsewhere). No wrong fact reached the final page this
time, but the gap is real and traces to Step 1's Jira-cross-check paragraph not mentioning
result-completeness verification — logged as a new, un-actioned follow-up finding for a
future pass, not folded into this release.

## [0.1.21] — 2026-08-04

`jira-content`: closed 2 real defects found via a fixture-eval + `kbg:review-fixtures` +
`kbg:iterate-skill` loop (3 evals × with/without skill, 3 iterations, 2 independent
reviewers per round). Iteration 1's review found a CRITICAL — a Bug's resolved-metadata
preview table stated Labels as `bug, billing, csv-export`, but the actual rendered
command (both the acli `-l` flag and the MCP `additional_fields.labels` payload) silently
dropped `bug`, carrying only the two domain tags — and a MAJOR: the project-key guard
asked the user to pick from all 11 visible Jira projects without first checking which
support the requested issue type, where a blind pick could dead-end on a project that
can't even hold a Story. Iteration 2's fix (a Step 4 cross-check between the stated
metadata table and the actual rendered payload; a proactive issue-type check before
asking) closed both, confirmed by two more independent reviewers each independently
re-running the live checks against production — but surfaced 2 new, narrower MAJORs in
the same fixture set: a non-default MCP draft option set `cloudId` to the site hostname
instead of the resolved GUID (the new cross-check was scoped to table-displayed fields
only, missing payload-only ones), and no documented rule distinguished when a
user-stated value forces the whole create over to MCP vs. when an agent-inferred value
doesn't — producing two individually-defensible but undocumented-as-consistent backend
choices across sibling evals. Iteration 3's fix (extended the cross-check to
payload-only values like `cloudId`; added an explicit "user-stated vs. agent-inferred"
rule to Step 5) closed both, independently re-verified live by both reviewers — but the
same round surfaced a CRITICAL, unrelated to this iteration's own diff: the
blocker-comment eval's `with_skill` output shipped an unflagged fabricated claim
("other QA work sharing the same environment is also stalled," unsupported by the
ticket or the user's request) in content that would post to a real production ticket if
approved, plus a disclosure regression versus the prior iteration's equivalent run (an
internally-reasoned Backlog/checklist-status tension was never surfaced to the user this
time). Per the loop's iteration cap (3), this fix session stops here — the confirmed
labels/project-guard/cloudId/backend-default fixes are kept; the comment-fabrication gap
traces to `templates/comments.md`'s ground rules ("never invent a value" is currently
scoped explicitly to the date field only, not generalized to impact-content) and is
logged as a new, un-actioned follow-up finding for a future pass, not folded into this
release.

## [0.1.20] — 2026-08-04

`acli`: closed a routing gap found via a 2-agent adversarial fixture review
(`kbg:review-fixtures`) and closed via a 3-iteration verify loop
(`kbg:iterate-skill`) — a templated comment task (status update / QA
verification / blocker / decision record) could reach `md2adf.py` directly
without ever routing to `jira-content` for the template shape, even though
the Core Loop named the routing rule. The first fix attempt (a code-comment
STOP directive at the point of use) was verified insufficient: a with-skill
fixture agent read it, correctly identified a "blocker" comment as one of
the four named types, then rationalized past it (session justifications:
"the user specified exact wording," "`jira-content` isn't loaded this
session," a misapplied carve-out). The working fix moved the guard to a
top-level blockquote — matching the file's existing, empirically-effective
guard for the analogous create-time bypass — and explicitly forecloses each
of the three rationalizations found. Verified via two more fixture-review
rounds, including a live read-only check against production Jira confirming
no comment was ever actually posted during testing. Also added a
shell-quoting note for `--jql`/file-path arguments (a zero-guidance gap the
same review surfaced); this fix's own effectiveness has not yet been
independently re-verified for its narrower residual case (an unquoted
user-facing command string) and should not be assumed fully closed.

## [0.1.19] — 2026-07-25

Empirical review pass (test agents drafting real tickets end-to-end + adversarial
cross-file reviewers, zero production Jira/Confluence contact) over `confluence-content`
and `jira-content`, fixing 18 confirmed defects total:

`confluence-content`: hardened the macro-safety check to distinguish a genuine
"no macros" result from a silent script error, fixed a stale `confluence space
view --key` vs `--id` drift (now `acli/ISSUES.md` Issue 8), added missing test
coverage for `inject-mermaid-macros.py`, corrected a couple of stale doc claims.

`jira-content`: closed contradictions between the two Bug/Story content paths
(guided `.md` vs. direct-payload `.json`) — `bug.payload.json` asked for
env/version text that `bug.md` explicitly says belongs only in Jira's native
field; `story.payload.json` had no Scope section and no standalone Impact
section despite both being required; `story.payload.json`'s 3rd Acceptance
Criteria placeholder literally invited dropping below Story's 3-AC minimum.
Also: added a guard against silently defaulting non-Tathep work to the `TP`
project, documented that full-body description replaces can silently drop
table/panel/expand nodes (same defect class as the confluence-content fix),
added the missing `-P`/parent flag to the Sub-task creation example, corrected
an overstated claim about `--assignee`'s accountId behavior, and documented an
offline (zero-production-contact) way to test the description edit-merge logic.

## [0.1.18] — 2026-07-16

Added two dispatchable specialist subagents, `agents/jira-expert.md` and
`agents/confluence-expert.md`, wrapping the existing skills for non-trivial
multi-step work (bulk triage, multi-section ticket authoring, Spec/PRD
drafting) without the caller driving every `acli`/skill call by hand.

Each preloads its two skills via the frontmatter `skills:` field —
`jira-expert`: `jira-acli:acli` + `jira-acli:jira-content`; `confluence-expert`:
`jira-acli:acli` + `jira-acli:confluence-content` — rather than restating their
content, same "referenced, never duplicated" rule the templates already
follow. Both are **preview-then-stop**: neither holds MCP tools, and neither
fires a mutating `acli` command itself — this environment's `acli`/MCP calls
hit real production Jira/Confluence, so each agent drafts the payload, renders
it, and returns the exact command/call for the main thread to run after
review. Product boundary is a hard rule in both files (each defers the other
product's work to its sibling agent), mirroring the skill split's
one-decision-one-owner shape.

CLAUDE.md and README.md updated for the new `agents/` convention; both plugin
manifests' descriptions updated to mention the two agents.
