---
name: jira-content
description: "Create or edit template-shaped Jira content — Bug/Story/Task/Epic/Sub-task descriptions and templated comments (status update/QA verification/blocker/decision record) — against the team's REQUIRED formats (Head of Engineering standard: GWT Acceptance Criteria, Thai PO/QA structure), no matter whether acli or the Atlassian MCP ends up doing the write. Trigger on ANY intent to create/file/open/log/report/raise a bug, defect, issue, story, task, epic, or sub-task, or to write/format/fix a Jira issue's description or a structured comment — in Thai or English, not just literal phrases like 'สร้างบั๊ก'/'สร้าง story' (also matches 'file a bug for X', 'open a ticket about Y', 'add a status update to TP-123'). Use this BEFORE calling `acli jira workitem create/edit` or any Jira-create MCP tool directly — never hand-build template-shaped content. Don't use for Confluence pages/specs/PRDs (see jira-acli:confluence-content), or for search, view, transition, link, clone, bulk ops, JQL export, Confluence blog/space/admin, or a trivial one-line comment (see jira-acli:acli)."
---

# Jira Content

Create or edit the **content** of a Jira Bug/Story/Task/Epic/Sub-task, or a templated comment —
against the team's canonical templates. Defaults to the **TP board** when the user doesn't name a
project, but works on any project / Atlassian site. Jira only — Confluence pages/specs are
`jira-acli:confluence-content`'s job, a different product with a different content shape.

**Backend: acli-first with Atlassian MCP fallback** — `jira-acli:acli` is the mechanical tool this
skill drives (search, auth, ADF conversion, create/edit calls); it owns none of the content
standard. This skill owns *what goes in the body*. Templates live in
`${CLAUDE_SKILL_DIR}/templates/` — see [`templates/README.md`](templates/README.md) for the full
index.

## When to use this skill vs acli vs confluence-content

- **Use this skill** for creating or editing the content of a Jira Bug/Story/Task/Epic/Sub-task, or
  a templated comment — anything that must match a team template.
- **Use `jira-acli:confluence-content`** for a Confluence Spec/PRD page — Confluence work, not
  Jira work.
- **Use `jira-acli:acli`** for search, view, transition, link, clone, bulk ops, JQL export,
  Confluence blog/space/admin ops, or a trivial one-line comment — mechanical work that isn't
  about shaping content to a template.

## Step 1 — Pick the type and gather

| What | Template | Gather |
|---|---|---|
| Bug | `templates/bug.md` | Guided — ask its gather questions |
| Story | `templates/story.md` | Guided — ask its gather questions |
| Task | `templates/task.payload.json` | No guided script — ask for the fields in `templates/README.md` § Task |
| Epic | `templates/epic.payload.json` | Same — `templates/README.md` § Epic |
| Sub-task | `templates/subtask.payload.json` | Same — `templates/README.md` § Sub-task; needs a parent key |
| Templated comment | `templates/comments.md` | Ask which of the 4 (status/QA/blocker/decision), then its fields |

Determine the type from the request; if ambiguous, ask once. Load the matching template:

```bash
cat "${CLAUDE_SKILL_DIR}/templates/bug.md"          # or story.md / comments.md
cat "${CLAUDE_SKILL_DIR}/templates/task.payload.json"   # Task/Epic/Sub-task: payload directly
```

Ask its gather questions **all at once, not one by one**. If the user already provided enough
context, skip to Step 2.

## Step 2 — Format the content

Write the body in **Thai** using the matching template from Step 1. **Acceptance Criteria
format/register/coverage rules are canonical in one place —
[`../../templates/acceptance-criteria.md`](../../templates/acceptance-criteria.md) — never restate
them here, just apply them.**

## Step 3 — Resolve issue metadata

*(Skip for comments.)*

Resolve at runtime; never hardcode IDs except the default project key `TP`.

| Field | Resolution |
|---|---|
| **Site** | Check `acli jira auth status` to find the authed site. For MCP fallback, use `mcp__plugin_atlassian_atlassian__getAccessibleAtlassianResources`. Ask if several. |
| **Project key** | User request; default `TP`. Validate via `mcp__plugin_atlassian_atlassian__getVisibleJiraProjects` before create. |
| **Issue type** | Matches the type picked in Step 1 (`Bug`/`Story`/`Task`/`Epic`/`Sub-task`). Confirm via `mcp__plugin_atlassian_atlassian__getJiraProjectIssueTypesMetadata` if create rejects. |
| **Priority** | **Bug:** money/data loss/blocked workflow → `High`; functional with workaround → `Medium`; cosmetic → `Low`. **Others:** `Medium` unless user specifies otherwise. Confirm if unsure. |
| **Labels** | `bug` + 1-2 domain tags (Bug); 1-2 domain tags (others, e.g. billing, refund, credit, player). Do NOT auto-add PO/QA labels. |
| **Environment** *(Bug only)* | Native Jira field. Set to prod/staging/local. Wrap in ADF for MCP fallback (see Step 5). |
| **Affects versions** *(Bug only)* | Only if user gives a valid version; validate or omit. |
| **Parent** *(Sub-task only)* | Required — resolve the parent issue key; sub-tasks cannot be created without one. |
| **Assignee** | Leave unassigned by default. Only set if user explicitly names one; resolve via `mcp__plugin_atlassian_atlassian__lookupJiraAccountId` (pass `cloudId` + `searchString`), then set `assignee_account_id`. |

## Step 4 — Preview and confirm

Before showing the preview, verify each gate in order:

1. If the type has an Acceptance Criteria section, confirm it covers error + boundary + regression
   paths, not just the happy path (see `../../templates/acceptance-criteria.md`).
   Failure mode to avoid: never file a ticket whose AC a QA can't verify against — if the AC
   drifts into implementation detail or omits the error case, the ticket fails review.
2. Show resolved metadata + Thai title + rendered content + chosen backend path as a review surface.
3. Create/send **only on the user's explicit go-ahead** — this preview-and-confirm gate is the
   safeguard against unwanted writes.

## Step 5 — Create

Default to `acli`. Fall back to the Atlassian MCP only when `acli` is unavailable, unauthenticated,
or cannot set a required field.

### 5a — Jira issue via acli (default)

Check auth first:
```bash
acli jira auth status
```

If authed, build the create payload from the Thai Markdown content (Bug/Story), or use the
payload template directly (Task/Epic/Sub-task):
```bash
# Bug/Story — guided Markdown → ADF
bash "${CLAUDE_SKILL_DIR}/scripts/md2adf.sh" /tmp/ticket.md \
  -s "<Thai summary>" -p <projectKey> -t <Bug|Story> -l "<labels>" > /tmp/wi.json

# Task/Epic/Sub-task — fill templates/*.payload.json placeholders directly, or convert Markdown:
bash "${CLAUDE_SKILL_DIR}/scripts/md2adf.sh" /tmp/ticket.md \
  -s "<summary>" -p <projectKey> -t <Task|Epic|Sub-task> -l "<labels>" > /tmp/wi.json
```

Then create:
```bash
acli jira workitem create --from-json /tmp/wi.json --json
```

Capture the returned key and reply: `✅ Created [PROJ-XXX](https://<site>.atlassian.net/browse/PROJ-XXX)`

> acli sets summary, description, project, type, and labels. If the user also needs `priority`,
> `environment`, `versions`, `parent`, or `assignee` set at create time and acli cannot satisfy
> one of them, switch to the MCP fallback for that field.

### 5b — Jira issue MCP fallback

Use when acli is not available, not authed, or cannot set a field. Call
`mcp__plugin_atlassian_atlassian__createJiraIssue`:

```
cloudId:       <resolved>
projectKey:    <resolved>
issueTypeName: "Bug" | "Story" | "Task" | "Epic" | "Sub-task"
summary:       <Thai title>
description:   <formatted Thai content>
contentFormat: "markdown"
additional_fields: {
  "priority": { "name": <derived> },
  "labels": [<domain tags>],
  // Bug only:
  "environment": { "version": 1, "type": "doc", "content": [
    { "type": "paragraph", "content": [{ "type": "text", "text": "prod" }] }
  ]},
  "versions": [{ "name": <version> }],   // Affects Version/s, NOT fixVersions (Fix Version/s) — different Jira fields; omit if unvalidated
  // Sub-task only:
  "parent": { "key": <parentKey> }
}
# assignee_account_id: OMIT by default. Include ONLY if user named an assignee.
```

After creation reply: `✅ Created [PROJ-XXX](https://<site>.atlassian.net/browse/PROJ-XXX)`

### 5c — Templated comment (on an existing ticket)

```bash
bash "${CLAUDE_SKILL_DIR}/scripts/md2adf.sh" note.md > /tmp/note.json   # bare doc mode — no -s/-p/-t
acli jira workitem comment create --key KEY-1 --body-file /tmp/note.json
```

## Editing an existing Jira issue's description

Template-conforming edits — fixing a description that doesn't match team format, adding a missing
AC, appending a status update — use acli's read-modify-write scripts. **Never** blind-replace with
a bare `acli jira workitem edit --description` (that flag wraps plain text into one literal ADF
paragraph — see `jira-acli:acli` § Description format).

```bash
# Append, or replace/remove one section by heading — preserves the rest of the body:
bash "${CLAUDE_SKILL_DIR}/scripts/acli-edit.sh" KEY notes.md
bash "${CLAUDE_SKILL_DIR}/scripts/acli-edit.sh" KEY --replace-section "🧪 เกณฑ์การยอมรับ" new-ac.md

# Full replace (only when the whole body needs to be rebuilt from a template):
bash "${CLAUDE_SKILL_DIR}/scripts/acli-set-desc.sh" KEY desc.md
```

Same preview-and-confirm gate as create: render the new body (both scripts support `--dry-run`),
show it, edit only on the user's explicit go-ahead.

## Input Contract

- **Required (Bug):** Thai bug summary, actual behavior, expected behavior, numbered reproduction steps, impact, environment.
- **Required (Story):** Thai feature summary, business reason, desired behavior, in/out scope, acceptance criteria.
- **Required (Task/Epic/Sub-task):** summary, context/goal, scope, acceptance/success criteria per `templates/README.md`; Sub-task also needs a parent.
- **Required (templated comment):** which of the 4 templates, and its fields.
- **Optional:** evidence (Bug), affected version (Bug), PO decision points (Story), explicit project key (defaults to `TP`), explicit assignee.
- **Tooling:** prefers `acli` when installed and authed; falls back to Atlassian MCP. If neither is available, ask the user to run `acli jira auth login` or enable the Atlassian MCP.

## Output Format

- **Preview:** site, project, issue type, priority, labels, assignee (if any), Thai title, rendered content, chosen backend.
- **Result:** issue key + URL, or comment confirmation.

## Failure Modes

- `acli` not installed or not authed; prompt to auth or fall back to MCP.
- Project key or issue type does not exist on the resolved site.
- `environment` field rejected as plain string (Bug); retry with ADF wrapper.
- `versions` value not found (Bug); omit and retry.
- Sub-task create rejected for missing/invalid parent; resolve the parent key and retry.
- Assignee email cannot be resolved; leave unassigned.
- User does not confirm at preview gate — creation/edit is skipped.

## Related

- `jira-acli:acli` — search, view, edit, transition, bulk ops, Confluence blog/space/admin, ADF↔markdown conversion. The backend tool this skill invokes — it owns no content standard.
- `jira-acli:confluence-content` — Confluence Spec/PRD page content. The Confluence-side counterpart to this skill.
- `atlassian:triage-issue` — de-duping/triaging before filing (needs the official Atlassian plugin installed).
