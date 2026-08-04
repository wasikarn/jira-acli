# Changelog

All notable changes to `jira-acli` are documented here. Format loosely follows
[Keep a Changelog](https://keepachangelog.com/); versions follow [SemVer](https://semver.org/).

Pre-`1.0.0`: breaking changes may land in any `0.x` release.

This file starts at `0.1.18` — releases before that predate the changelog. See
`git log` for the full history back to `0.1.0`.

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
