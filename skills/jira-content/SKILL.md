---
name: jira-content
description: "Create or edit template-shaped Jira content — Bug/Story/Task/Epic/Sub-task descriptions and templated comments (status update/QA verification/blocker/decision record) — against the team's REQUIRED formats (Head of Engineering standard: GWT Acceptance Criteria, Thai PO/QA structure), no matter whether acli or the Atlassian MCP ends up doing the write. Trigger on ANY intent to create/file/open/log/report/raise a bug, defect, issue, story, task, epic, or sub-task, or to write/format/fix a Jira issue's description or a structured comment — in Thai or English, not just literal phrases like 'สร้างบั๊ก'/'สร้าง story' (also matches 'file a bug for X', 'open a ticket about Y', 'add a status update to TP-123'). Use this BEFORE calling `acli jira workitem create/edit` or any Jira-create MCP tool directly — never hand-build template-shaped content. Don't use for Confluence pages/specs/PRDs (see jira-acli:confluence-content), or for search, view, transition, link, clone, bulk ops, JQL export, Confluence blog/space/admin, or a trivial one-line comment (see jira-acli:acli)."
---

# Jira Content

Create or edit the **content** of a Jira Bug/Story/Task/Epic/Sub-task, or a templated comment — against the team's canonical templates. Defaults to the **TP board** when the user doesn't name a project; works on any project / Atlassian site. Jira only — Confluence pages/specs are `jira-acli:confluence-content`'s job.

**Backend: acli-first with Atlassian MCP fallback** — `jira-acli:acli` is the mechanical tool this skill drives. This skill owns *what goes in the body*. Templates in `${CLAUDE_SKILL_DIR}/templates/` — see [`templates/README.md`](templates/README.md) for the index.

## When to use this skill vs acli vs confluence-content

- **This skill** — create/edit Jira Bug/Story/Task/Epic/Sub-task content or a templated comment.
- **`jira-acli:confluence-content`** — Confluence Spec/PRD page.
- **`jira-acli:acli`** — search, view, transition, link, clone, bulk ops, JQL export, Confluence blog/space/admin, trivial one-line comments.

## Step 1 — Pick the type and gather

| What | Template | Gather |
|---|---|---|
| Bug | `templates/bug.md` | Guided — ask its gather questions |
| Story | `templates/story.md` | Guided — ask its gather questions |
| Task | `templates/task.payload.json` | No guided script — fields in `templates/README.md` § Task |
| Epic | `templates/epic.payload.json` | Same — `templates/README.md` § Epic |
| Sub-task | `templates/subtask.payload.json` | Same — `templates/README.md` § Sub-task; needs a parent key |
| Templated comment | `templates/comments.md` | Ask which of the 4 (status/QA/blocker/decision), then its fields |

```bash
cat "${CLAUDE_SKILL_DIR}/templates/bug.md"          # or story.md / comments.md
cat "${CLAUDE_SKILL_DIR}/templates/task.payload.json"   # Task/Epic/Sub-task: payload directly
```

Ask all gather questions **at once, not one by one**. If the user already provided enough, skip to Step 2.

## Step 2 — Format the content

Write the body in **Thai** using the matching template. **AC format/register/coverage rules are canonical in [`../../templates/acceptance-criteria.md`](../../templates/acceptance-criteria.md) — never restate them, just apply them.**

## Step 3 — Resolve issue metadata

*(Skip for comments.)* Resolve at runtime; never hardcode IDs except the default project key `TP`.

- **Site** — `acli jira auth status`. For MCP, `mcp__plugin_atlassian_atlassian__getAccessibleAtlassianResources`. Ask if several.
- **Project key** — User request; default `TP`. Validate via `acli jira project view <KEY>` before create. Fall back to `mcp__plugin_atlassian_atlassian__getVisibleJiraProjects` only if acli is unavailable/unauthed.
- **Issue type** — Matches Step 1's pick. acli has no issue-type-metadata command; confirm via `mcp__plugin_atlassian_atlassian__getJiraProjectIssueTypesMetadata` if create rejects.
- **Priority** — **Bug:** money/data-loss/blocked-workflow → `High`; functional w/ workaround → `Medium`; cosmetic → `Low`. **Others:** `Medium` unless user says otherwise.
- **Labels** — `bug` + 1-2 domain tags (Bug); 1-2 domain tags (others). Do NOT auto-add PO/QA labels.
- **Environment** *(Bug only)* — Native Jira field. prod/staging/local. Wrap in ADF for MCP fallback.
- **Affects versions** *(Bug only)* — Only if user gives a valid version; validate or omit.
- **Parent** *(Sub-task only)* — Required. Sub-tasks can't be created without one.
- **Assignee** — Leave unassigned by default. Only set if user names one. acli's `--assignee` only resolves `@me`/`default`/email; a raw accountId silently unassigns (see `acli/REFERENCE.md`). When email is privacy-hidden, resolve via `mcp__plugin_atlassian_atlassian__lookupJiraAccountId` (pass `cloudId` + `searchString`), then set `assignee_account_id`.

## Step 4 — Preview and confirm

Show resolved metadata + Thai title + rendered content + chosen backend as a review surface. If the type has an AC section, confirm it covers error + boundary + regression paths (see [`../../templates/acceptance-criteria.md`](../../templates/acceptance-criteria.md)). Create/send **only on the user's explicit go-ahead** — this gate is the safeguard against unwanted writes.

## Step 5 — Create

Default to `acli`. Fall back to Atlassian MCP only when acli is unavailable, unauthenticated, or cannot set a required field.

### 5a — Jira issue via acli (default)

```bash
acli jira auth status
# Bug/Story — guided Markdown → ADF
bash "${CLAUDE_SKILL_DIR}/scripts/md2adf.sh" /tmp/ticket.md \
  -s "<Thai summary>" -p <projectKey> -t <Bug|Story> -l "<labels>" > /tmp/wi.json
# Task/Epic/Sub-task — fill templates/*.payload.json placeholders directly, or convert Markdown:
bash "${CLAUDE_SKILL_DIR}/scripts/md2adf.sh" /tmp/ticket.md \
  -s "<summary>" -p <projectKey> -t <Task|Epic|Sub-task> -l "<labels>" > /tmp/wi.json

acli jira workitem create --from-json /tmp/wi.json --json
```

Reply: `✅ Created [PROJ-XXX](https://<site>.atlassian.net/browse/PROJ-XXX)`. If user also needs `priority` / `environment` / `versions` / `parent` / `assignee` at create time and acli can't satisfy one, switch to MCP for that field.

### 5b — Jira issue MCP fallback

Call `mcp__plugin_atlassian_atlassian__createJiraIssue`:

```
cloudId:       <resolved>
projectKey:    <resolved>
issueTypeName: "Bug" | "Story" | "Task" | "Epic" | "Sub-task"
summary:       <Thai title>
description:   <formatted Thai content>
contentFormat: "markdown"
parent:        <parentKey>   # Sub-task only — top-level param, plain issue key string, NOT nested in additional_fields
additional_fields: {
  "priority": { "name": <derived> },
  "labels": [<domain tags>],
  // Bug only:
  "environment": { "version": 1, "type": "doc", "content": [
    { "type": "paragraph", "content": [{ "type": "text", "text": "prod" }] }
  ]},
  "versions": [{ "name": <version> }]   # Affects Version/s, NOT fixVersions — omit if unvalidated
}
# assignee_account_id: OMIT by default. Include ONLY if user named an assignee.
```

Reply: `✅ Created [PROJ-XXX](https://<site>.atlassian.net/browse/PROJ-XXX)`.

### 5c — Templated comment (on an existing ticket)

```bash
bash "${CLAUDE_SKILL_DIR}/scripts/md2adf.sh" note.md > /tmp/note.json   # bare doc mode — no -s/-p/-t
acli jira workitem comment create --key KEY-1 --body-file /tmp/note.json
```

## Editing an existing Jira issue's description

Template-conforming edits — fixing a description that doesn't match team format, adding a missing AC, appending a status update — use acli's read-modify-write scripts. **Never** blind-replace with `acli jira workitem edit --description` (wraps plain text into one literal ADF paragraph — see `jira-acli:acli` § Description format).

```bash
bash "${CLAUDE_SKILL_DIR}/scripts/acli-edit.sh" KEY notes.md
bash "${CLAUDE_SKILL_DIR}/scripts/acli-edit.sh" KEY --replace-section "🧪 เกณฑ์การยอมรับ" new-ac.md
bash "${CLAUDE_SKILL_DIR}/scripts/acli-set-desc.sh" KEY desc.md   # full replace only
```

Same preview-and-confirm gate as create: render the new body (both scripts support `--dry-run`), show it, edit only on the user's explicit go-ahead.

## Editing an existing templated comment

Fixing/updating a comment that already follows one of the 4 `templates/comments.md` shapes — e.g. "แก้ comment สถานะล่าสุดให้หน่อย". **Never** hand this to acli's raw `comment update --body-adf` without going through the template first.

```bash
# 1. Read existing comment (find its id first if not given):
acli jira workitem view KEY --fields comment --json
# 2. Edit the Markdown per templates/comments.md (keep AC# numbering if it references the ticket's own AC). Preview before sending.
# 3. Re-convert and update (comment update needs --body-adf, not --body-file):
bash "${CLAUDE_SKILL_DIR}/scripts/md2adf.sh" note.md > /tmp/note.json
acli jira workitem comment update --key KEY --id <commentId> --body-adf /tmp/note.json
```

## Input Contract

- **Required (Bug):** Thai summary, actual behavior, expected behavior, numbered repro steps, impact, environment.
- **Required (Story):** Thai summary, business reason, desired behavior, in/out scope, AC.
- **Required (Task/Epic/Sub-task):** summary, context/goal, scope, AC per `templates/README.md`; Sub-task also needs a parent.
- **Required (templated comment):** which of the 4 templates, and its fields.
- **Optional:** evidence (Bug), affected version (Bug), PO decision points (Story), explicit project key (defaults `TP`), explicit assignee.
- **Tooling:** prefers `acli` when installed + authed; falls back to Atlassian MCP. If neither, ask the user to run `acli jira auth login` or enable the Atlassian MCP.

## Output Format

- **Preview:** site, project, issue type, priority, labels, assignee (if any), Thai title, rendered content, chosen backend.
- **Result:** issue key + URL, or comment confirmation.

## Failure Modes

- `acli` not installed or not authed → prompt to auth or fall back to MCP.
- Project key or issue type does not exist on the resolved site.
- `environment` rejected as plain string (Bug) → retry with ADF wrapper.
- `versions` value not found (Bug) → omit and retry.
- Sub-task create rejected for missing/invalid parent → resolve the parent key and retry.
- Assignee email cannot be resolved → leave unassigned.
- User does not confirm at preview gate → creation/edit is skipped.

## Related

- `jira-acli:acli` — search, view, edit, transition, bulk ops, Confluence blog/space/admin, ADF↔markdown. The backend tool this skill invokes.
- `jira-acli:confluence-content` — Confluence Spec/PRD page content. The Confluence-side counterpart.
- `atlassian:triage-issue` — de-duping/triaging before filing (needs the official Atlassian plugin).
