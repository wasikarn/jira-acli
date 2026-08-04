# Changelog

All notable changes to `jira-acli` are documented here. Format loosely follows
[Keep a Changelog](https://keepachangelog.com/); versions follow [SemVer](https://semver.org/).

Pre-`1.0.0`: breaking changes may land in any `0.x` release.

This file starts at `0.1.18` — releases before that predate the changelog. See
`git log` for the full history back to `0.1.0`.

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
