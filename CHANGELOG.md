# Changelog

All notable changes to `jira-acli` are documented here. Format loosely follows
[Keep a Changelog](https://keepachangelog.com/); versions follow [SemVer](https://semver.org/).

Pre-`1.0.0`: breaking changes may land in any `0.x` release.

This file starts at `0.1.18` — releases before that predate the changelog. See
`git log` for the full history back to `0.1.0`.

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
