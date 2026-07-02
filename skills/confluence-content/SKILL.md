---
name: confluence-content
description: "Create or edit the content of a Confluence Spec/PRD page against the team's canonical template (business reason, scope, per-requirement GWT Acceptance Criteria) — via the Atlassian MCP (acli's `confluence page` command is view-only, it can't create or update). Trigger on ANY intent to create/write/draft a Confluence page, spec, PRD, or design doc, or to edit/update/fix/revise an existing Confluence page's content — in Thai or English, not just literal phrases like 'สร้าง spec' (also matches 'write a spec for X', 'draft a PRD for Y', 'update the Confluence page for Z', 'add a section to the design doc'). Use this BEFORE calling createConfluencePage/updateConfluencePage directly — never hand-build the page body. Don't use for Jira issues (Bug/Story/Task/Epic/Sub-task/comments — see jira-acli:jira-content), Confluence blogs/spaces/admin ops, or viewing a page without editing it (see jira-acli:acli)."
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
| **Site / cloudId** | `mcp__plugin_atlassian_atlassian__getAccessibleAtlassianResources`. Ask if several. |
| **Space** | `mcp__plugin_atlassian_atlassian__getConfluenceSpaces`; ask the user if ambiguous. |
| **Parent page** | Only if the user wants this nested under an existing page; resolve its `pageId`. Omit for a top-level page. |
| **Title** | From the spec's subject; confirm with the user. |

## Step 4 — Preview and confirm

1. Confirm each requirement's Acceptance Criteria covers error + boundary + regression paths, not
   just the happy path (see `../../templates/acceptance-criteria.md`).
2. Show resolved metadata (site, space, parent, title) + rendered Thai content as a review surface.
3. Create/update **only on the user's explicit go-ahead** — this preview-and-confirm gate is the
   safeguard against unwanted writes. `createConfluencePage`/`updateConfluencePage` have no dry-run.

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

## Editing an existing page

There's no append/patch mechanism for Confluence (unlike `jira-content`'s `acli-edit.sh` for Jira)
— `updateConfluencePage` always replaces the **entire** body, so the flow is a manual
read-modify-write, not a script:

```
1. mcp__plugin_atlassian_atlassian__getConfluencePage
     cloudId: <resolved>  pageId: <id or tiny-link>  contentFormat: "markdown"
   → read the current body as Markdown.

2. Apply the edit to that Markdown (fix a section, add a missing AC, etc.) — keep the rest
   of the page unchanged. If the page doesn't already follow templates/confluence-spec.md,
   reshape it to match while editing, don't perpetuate the drift.

3. mcp__plugin_atlassian_atlassian__updateConfluencePage
     cloudId: <resolved>  pageId: <same id>  title: <keep or update>
     body: <the full new Markdown — step 1's body with the edit applied>
     contentFormat: "markdown"
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
