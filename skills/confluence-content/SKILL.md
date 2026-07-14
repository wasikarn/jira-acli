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
| **Site / cloudId** | Re-derive against `acli/REFERENCE.md` + `acli/SKILL.md` § "When acli can't" before naming any `mcp__...` tool here. cloudId is MCP-only — resolve via `mcp__plugin_atlassian_atlassian__getAccessibleAtlassianResources`. Ask if several. |
| **Space** | `acli confluence space list --json` / `acli confluence space view --key <KEY> --json` — acli has full space CRUD. Fall back to `mcp__plugin_atlassian_atlassian__getConfluenceSpaces` only if acli can't find it. Ask the user if ambiguous. |
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
`/mermaid` command, like TP-807's 7 diagrams — is left exactly as-is, not retroactively wrapped.
The script's default constants (extension key, cloud ID, account ID, workspace ARI) are specific to
this site/author — see the script's own docstring for how to re-derive them if pointed at a
different Atlassian site. If the target site doesn't have this app installed, the mermaid code
blocks still render as readable syntax-highlighted text — degrade gracefully, don't treat the macro
step as required.

## Editing an existing page

There's no append/patch mechanism for Confluence (unlike `jira-content`'s `acli-edit.sh` for Jira)
— `updateConfluencePage` always replaces the **entire** body, so the flow is a manual
read-modify-write, not a script:

```
1. acli first — acli's `confluence page` is only view-*write*-blocked, reads work fine:
   acli confluence page view --id <id> --body-format atlas_doc_format --json \
     | python3 -c "import json,sys; print(json.load(sys.stdin)['body']['atlas_doc_format']['value'])" \
     | python3 "${CLAUDE_SKILL_DIR}/../acli/scripts/adf2md.py" -
   → read the current body as Markdown. Falls back to
   mcp__plugin_atlassian_atlassian__getConfluencePage (cloudId, pageId,
   contentFormat: "markdown") only if acli is unavailable/unauthed.

2. Apply the edit to that Markdown (fix a section, add a missing AC, etc.) — keep the rest
   of the page unchanged. If the page doesn't already follow templates/confluence-spec.md,
   reshape it to match while editing, don't perpetuate the drift.

3. mcp__plugin_atlassian_atlassian__updateConfluencePage
     cloudId: <resolved>  pageId: <same id>  title: <keep or update>
     body: <the full new Markdown — step 1's body with the edit applied>
     contentFormat: "markdown"
   — genuine MCP-only step, acli's confluence page command cannot write.
```

Same preview-and-confirm gate as create: show the diff between step 1's body and step 2's edited
version, update only on the user's explicit go-ahead.

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

## Related

- `jira-acli:jira-content` — Jira Bug/Story/Task/Epic/Sub-task content and templated comments. The
  Jira-side counterpart to this skill.
- `jira-acli:acli` — Confluence blog/space/admin ops, search, and view. Doesn't touch page content.
- `atlassian:spec-to-backlog` — converting a Confluence Spec/PRD page into a backlog of epics +
  tickets (needs the official Atlassian plugin installed).
