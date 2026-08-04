---
name: confluence-content
description: "Create or edit the content of a Confluence Spec/PRD page against the team's canonical template (business reason, scope, per-requirement GWT Acceptance Criteria) — via the Atlassian MCP (acli's `confluence page` command is view-only, it can't create or update). Use this BEFORE calling createConfluencePage/updateConfluencePage directly — never hand-build the page body."
when_to_use: "Trigger on ANY intent to create/write/draft a Confluence page, spec, PRD, or design doc, or to edit/update/fix/revise an existing Confluence page's content — in Thai or English, not just literal phrases like 'สร้าง spec' (also matches 'write a spec for X', 'draft a PRD for Y', 'update the Confluence page for Z', 'add a section to the design doc'). Don't use for Jira issues (Bug/Story/Task/Epic/Sub-task/comments — see jira-acli:jira-content), Confluence blogs/spaces/admin ops, or viewing a page without editing it (see jira-acli:acli)."
---

# Confluence Content

Create or edit the **content** of a Confluence Spec/PRD page — against the team's canonical
template. Jira and Confluence are different products with different content shapes; this skill
owns Confluence only. Jira issue content is `jira-acli:jira-content`'s job.

**Backend: Atlassian MCP only** — acli's `confluence page` command is view-only, so
`createConfluencePage`/`updateConfluencePage` are the only way to create or update a page. There is
no acli path here, unlike Jira. Template lives at
[`templates/confluence-spec.md`](templates/confluence-spec.md).

## When to use this skill vs acli vs jira-content

- **Use this skill** for creating or editing the content of a Confluence Spec/PRD page.
- **Use `jira-acli:jira-content`** for Jira Bug/Story/Task/Epic/Sub-task content or templated
  comments — Jira work, not Confluence work.
- **Use `jira-acli:acli`** for Confluence blog/space/admin ops, or viewing a page without editing
  its content.

## Step 1 — Gather

```bash
cat "${CLAUDE_SKILL_DIR}/templates/confluence-spec.md"
```

Ask per section: business reason, scope, each requirement (R1/R2…) as its own user story with its
own Acceptance Criteria. Ask all at once, not one by one. If the user already provided enough
context, skip to Step 2.

Before drafting Requirements/AC for any page that asserts specific facts about how a system
behaves — a new feature Spec, but also a runbook, an architecture doc, or existing-behavior
documentation that happens to use the Spec template's Requirements/AC structure — a quick Jira
search (`acli jira workitem search --jql "..."`) for adjacent or related tickets is worth doing
first, even though this skill owns Confluence content, not Jira content. The domain facts that
shape a page's Acceptance Criteria often live in Jira, not in what the user typed — e.g. whether
the underlying system processes the thing continuously or in discrete steps changes what a
boundary/regression AC should assert, and specific numbers (retry counts, timeouts, thresholds)
stated as fact rather than flagged as placeholders can be wrong in exactly the way Jira would have
caught.

This search is easy to under-verify precisely because it's secondary to the page draft, not the
task itself — confirmed gap (2026-08-04): a fixture run's search reported "30 hits" and moved
straight to drafting without noticing `acli`'s own `--json`/`--csv` output silently caps at ~30
rows (documented in `jira-acli:acli`'s SKILL.md); the true count was 395. No wrong fact reached
the final page that time, but most of the matching tickets were never actually read. Before
treating this search's result as the full picture, cross-check with `--count` or re-run with
`--paginate` — same discipline `acli` already documents for its own reads, worth restating here
because attention naturally goes to the page you're writing, not the research step feeding it.

Don't skip this because the page technically isn't a "new feature" — "this is documenting existing
behavior, not proposing something new" is not an exemption; existing-behavior claims are exactly
the kind of thing Jira tickets (bug reports, prior implementation tickets) tend to correct or
contradict. Confirmed gap (twice): one fixture run skipped this and produced a Spec with an AC
implying continuous tracking for a system that actually processes spend in discrete booking
increments; a second run reasoned its way past this exact rule ("this isn't really a Spec") and
then invented every retry/backoff number in its Requirements/AC instead of running one read-only
search. This is research, not authoring — any actual Jira write still routes through
`jira-acli:jira-content`.

## Step 2 — Format the content

Write the body in **Thai** using `templates/confluence-spec.md`. **Acceptance Criteria
format/register/coverage rules are canonical in one place —
[`../../templates/acceptance-criteria.md`](../../templates/acceptance-criteria.md) — never restate
them here, just apply them.**

⚠️ This template is a **starting proposal**, adapted from the Story template — not mined from real
Confluence usage or confirmed as a Head-of-Engineering standard. Revise once used in practice.

## Step 3 — Resolve page metadata

Resolve at runtime; never hardcode IDs.

| Field | Resolution |
|---|---|
| **Site / cloudId** | Re-derive against `acli/REFERENCE.md` + `acli/SKILL.md` § "When acli can't" before naming any `mcp__...` tool here. cloudId is MCP-only — resolve via `mcp__plugin_atlassian_atlassian__getAccessibleAtlassianResources`. Ask if several. **If you're an MCP-less caller (e.g. the `confluence-expert` agent, which holds no MCP tools by design)**, this field can never be resolved locally — name it as an outstanding gap in your handoff instead of guessing or skipping it. |
| **Space** | `acli confluence space list --json` to resolve — acli has full space CRUD, but inconsistently: `create`/`archive`/`update`/`restore` all take `--key`, `view` alone takes `--id` (`space view --key` fails `✗ unknown flag: --key`, confirmed live 2026-07-24). ⚠️ **`--keys <KEY>` does not filter** — confirmed live 2026-08-04: it returns the same full unfiltered space list whether passed or omitted. Don't grab `.results[0].id` — match the target `key` explicitly instead: `acli confluence space list --json \| python3 -c "import json,sys; d=json.load(sys.stdin); print([r['id'] for r in d['results'] if r['key']=='<KEY>'][0])"`. Then `space view --id <id> --json` only if you need more than list already returned. Fall back to `mcp__plugin_atlassian_atlassian__getConfluenceSpaces` only if acli can't find it. Ask the user if ambiguous. |
| **Parent page** | Only if the user wants this nested under an existing page; resolve its `pageId`. Omit for a top-level page. |
| **Title** | From the spec's subject; confirm with the user. |

## Step 4 — Preview and confirm

Show resolved metadata (site, space, parent, title) + rendered Thai content as a review surface. Confirm each requirement's AC covers error + boundary + regression paths (see `../../templates/acceptance-criteria.md`). Create/update **only on the user's explicit go-ahead** — `createConfluencePage`/`updateConfluencePage` have no dry-run.

## Step 5 — Create

```
mcp__plugin_atlassian_atlassian__createConfluencePage
  cloudId:       <resolved>
  spaceId:       <resolved>
  title:         <spec title>
  body:          <filled-in templates/confluence-spec.md>
  contentFormat: "markdown"
  contentType:   "page"
  parentId:      <resolved, if nesting under an existing page — omit otherwise>
```

Reply: `✅ Created <title> — <page URL>`

## Embedding Mermaid diagrams

A plain ` ```mermaid ` fenced code block in `contentFormat: "markdown"` converts cleanly to a
native Confluence `code` macro (language=mermaid, wide breakout) — but that only gets you
**syntax-highlighted text**. Confluence Cloud has no built-in Mermaid renderer. If the target site
has the **"Mermaid diagram"** marketplace app installed (a Forge custom-UI macro,
`extension-type: com.atlassian.ecosystem` — confirmed installed on `100-stars.atlassian.net`,
space `BEP`), each code block needs a **separate macro instance immediately after it** to actually
render as a diagram — one macro renders one code block, it does not scan the whole page.

⚠️ **Use `contentFormat: "adf"` for the fetch-inject-write cycle below — never `"html"`.** Writing
the macro through `updateConfluencePage(contentFormat="html")` makes Confluence's html-writer
"helpfully" restructure a code-block-then-matching-extension-macro pattern into three nodes (a
broken preview extension, the code wrapped in a collapsible `expand`, then the original extension)
— the diagram renders TWICE with a stray collapsed accordion between them. Confirmed broken by
visual screenshot 2026-07-14. Writing the identical macro as a proper ADF `extension` node via
`contentFormat="adf"` does not trigger this — confirmed by both a structural read-back and a
screenshot, same day, same page: one clean render per diagram, no wrapping, no duplication.

```bash
# 1. Write/update the page normally first (Step 5, or the edit flow below) with the
#    mermaid fences included as plain ```mermaid code blocks in the Markdown body.
# 2. Fetch the page back as ADF (structured JSON, round-trip-safe) and inject the render
#    macro after every mermaid code block that doesn't already have one:
#    mcp__...__getConfluencePage(cloudId, pageId, contentFormat="adf")  -> save full response to page.json
python3 "${CLAUDE_SKILL_DIR}/scripts/inject-mermaid-macros.py" page.json --page-id <id> > doc.json
# 3. Write the script's output straight back as the body (it's already a bare {"type":"doc",...}):
#    mcp__...__updateConfluencePage(cloudId, pageId, body=<doc.json content>, contentFormat="adf")
```

Idempotent — safe to re-run after adding more diagrams to a page that already has some rendered;
existing macros are left untouched and not double-counted. By default a newly-decorated code block
is wrapped in a collapsible `expand` section (title "Diagram source", collapsed on load for every
viewer — see `--collapse-title` to change the label) so the page shows the rendered diagram with
the raw syntax tucked behind a click, not a wall of mermaid text above every diagram. A code block
already followed by a bare (unwrapped) macro — e.g. one inserted natively via the editor's
`/mermaid` command before this script ever touched the page — is left exactly as-is, not
retroactively wrapped.
The script's default constants (extension key, cloud ID, account ID, workspace ARI) are specific to
this site/author — see the script's own docstring for how to re-derive them if pointed at a
different Atlassian site. If the target site doesn't have this app installed, the mermaid code
blocks still render as readable syntax-highlighted text — degrade gracefully, don't treat the macro
step as required.

## Editing an existing page

There's no append/patch mechanism for Confluence (unlike `jira-content`'s `acli-edit.sh` for Jira)
— `updateConfluencePage` always replaces the **entire** body, so the flow is a manual
read-modify-write, not a script:

⚠️ **Check for macros BEFORE picking a write format — `contentFormat: "markdown"` silently
deletes them.** Plain Markdown has no syntax for a Forge macro (`extension` node) or a collapsible
`expand` wrapper, so a markdown-format `updateConfluencePage` full-body-replace drops every macro
on the page without warning or error — the write succeeds, the page just loses them. Confirmed
2026-07-14 on TP-807: a prose-only edit (fixing word choice, no diagram changes intended) wiped all
7 native "Mermaid diagram" render macros the page had; only caught because the user noticed the
diagrams had vanished on the live page. Fetch the page as ADF first and check for `extension`/
`expand` nodes — if any exist, the edit **must** go out as `contentFormat: "adf"` (fetch → apply
the edit to the ADF JSON directly, or re-run `scripts/inject-mermaid-macros.py` after a markdown
round-trip to re-add what a markdown write would drop — see "Embedding Mermaid diagrams" above),
never `"markdown"`. Markdown is only safe when the page has zero macro/expand nodes.

```
1. acli first — acli's `confluence page` is only view-*write*-blocked, reads work fine:
   acli confluence page view --id <id> --body-format atlas_doc_format --json \
     | python3 -c "import json,sys; print(json.load(sys.stdin)['body']['atlas_doc_format']['value'])" \
     > page.adf.json
   python3 "${CLAUDE_SKILL_DIR}/../acli/scripts/adf-node-diff.py" page.adf.json | grep -E "^(extension|expand):"
   → if either count is > 0, this page has macros — ADF write path only, skip step 3's markdown option.
   → empty output is only safe to read as "no macros" if adf-node-diff.py itself ran clean. It exits
   non-zero with FATAL on bad input, and that failure prints to stderr — stdout is empty either way, so
   an error and a genuinely macro-free page look identical if you only glance at the grep line. Check the
   exit code (or just look at stderr) before treating silence as a green light; on any error, re-fetch and
   re-check rather than defaulting to markdown.
   → this walks the ADF tree recursively (every depth, not just top-level) — a shallow top-level-only
   count would miss a macro nested inside a table cell, panel, or layout section and falsely green-light
   a markdown write, reproducing the exact 2026-07-14 incident below on a different page shape.
   python3 "${CLAUDE_SKILL_DIR}/../acli/scripts/adf2md.py" page.adf.json
   → read the current body as Markdown (for review/editing text — the ADF file is still the
   source of truth for the write). Falls back to mcp__plugin_atlassian_atlassian__getConfluencePage
   (cloudId, pageId, contentFormat: "markdown") only if acli is unavailable/unauthed — but that
   fallback can't detect macros either, so still fetch contentFormat: "adf" once to check.

2. Apply the edit. If the page has NO macros, edit the Markdown from step 1 directly (fix a
   section, add a missing AC, etc.) — keep the rest of the page unchanged. If the page doesn't
   already follow templates/confluence-spec.md, reshape it to match while editing, don't
   perpetuate the drift. If the page HAS macros, apply the edit to the ADF JSON's text nodes
   directly (or edit the markdown and re-run inject-mermaid-macros.py against the result) —
   never round-trip through a plain-markdown intermediate for the write itself.

2.5. Immediately before firing 3a/3b — not back at step 1 — re-fetch the page and check its
   version number (or, lacking that, its content) against what step 1 captured. The
   preview-and-confirm gate below can leave an arbitrarily long gap between the read and the
   write; a full-body replace after that gap will silently clobber any edit someone else made to
   the page in the interval, the same way a stale markdown write clobbers macros. If the version
   changed, stop — re-diff against the new content and re-preview rather than overwriting it.

3a. No macros — mcp__plugin_atlassian_atlassian__updateConfluencePage
     cloudId: <resolved>  pageId: <same id>  title: <keep or update>
     body: <the full new Markdown — step 1's body with the edit applied>
     contentFormat: "markdown"

3b. Has macros — mcp__plugin_atlassian_atlassian__updateConfluencePage
     cloudId: <resolved>  pageId: <same id>  title: <keep or update>
     body: <the full edited ADF JSON — step 2's output, a bare {"type":"doc",...} document>
     contentFormat: "adf"
   — either way, genuine MCP-only step, acli's confluence page command cannot write.

4. Verify: fetch the page back as ADF and diff its node count/types against what you sent —
   don't just check the prose rendered correctly. A macro-count check (extension/expand nodes,
   before vs. after) is the cheap, specific version of this for any page that had macros.
```

Same preview-and-confirm gate as create: show the diff between step 1's body and step 2's edited
version, update only on the user's explicit go-ahead.

## Known limitations

- **No script → live-write bridge for large bodies.** `createConfluencePage`/`updateConfluencePage`
  take `body` as a literal text parameter — there is no way to point the tool at a script's output
  file. Any script that produces a full-page body (e.g. `scripts/inject-mermaid-macros.py`) still
  needs its output file copied into the tool call by hand, however large the page — the MCP layer
  has no file-reference mechanism. Confirmed working this way on TP-807 (115K+ characters, 106
  top-level ADF nodes) 2026-07-14, but only because the write was verified afterward: fetch the live
  page back and diff its content against the script's own output file (see the diff pattern in
  `scripts/inject-mermaid-macros.py`'s usage). Treat that verification step as required, not
  optional, for any hand-copied write past a few KB — a silent transcription slip is otherwise
  undetectable. The real fix is a script that calls the Atlassian REST API directly (`curl` + an API
  token) instead of routing through the MCP tool's parameter — out of scope until a repeat pain
  point justifies building it.

## Input Contract

- **Required (create):** title, business reason, scope, at least one requirement with its own AC.
- **Required (edit):** the page (ID, tiny-link, or title to resolve) and what should change.
- **Optional:** parent page (for nesting), explicit space (asks if ambiguous).
- **Tooling:** Atlassian MCP only. If unavailable, ask the user to enable the Atlassian MCP plugin.

## Output Format

- **Preview:** site, space, parent (if any), title, rendered content — or, for an edit, a diff of
  the changed section(s).
- **Result:** page URL, or edit confirmation.

## Failure Modes

- Atlassian MCP not available; ask the user to enable it (no acli fallback exists for page create/update).
- Space not found or ambiguous; ask the user to confirm.
- Confluence page ID not found or ambiguous (title search returns >1 match); ask the user to
  confirm the page or paste its URL/tiny-link.
- User does not confirm at preview gate — creation/edit is skipped.
- The Mermaid embed sequence ("Embedding Mermaid diagrams" above) fails or is interrupted after
  the page write but before the inject-and-write-back step — the page is left with plain
  syntax-highlighted code blocks, not broken or partially corrupted. Re-run
  `scripts/inject-mermaid-macros.py` once ready; it's idempotent and leaves already-rendered
  diagrams untouched.
- A page's version changed between your initial read and your write (see "Editing an existing
  page" step 2.5) — stop and re-diff against the new content, don't overwrite it.

## Related

- `jira-acli:jira-content` — Jira Bug/Story/Task/Epic/Sub-task content and templated comments. The
  Jira-side counterpart to this skill.
- `jira-acli:acli` — Confluence blog/space/admin ops, search, and view. Doesn't touch page content.
- `atlassian:spec-to-backlog` — converting a Confluence Spec/PRD page into a backlog of epics +
  tickets (needs the official Atlassian plugin installed).
