# jira-content templates — the SSOT

Every template that defines what a created/edited Jira ticket or Confluence page should contain
lives here. `jira-acli:acli` is the mechanical backend these templates get sent through (ADF
conversion, `create --from-json`, MCP fallback) — it owns none of this content.

Files here:

- `acceptance-criteria.md` — **the** AC format/register/coverage rule. Every other file points here.
- `bug.md` / `story.md` — Thai, PO/QA-facing, guided single-ticket creation (used by this skill's
  Step 1–2 gather flow).
- `bug.payload.json` / `story.payload.json` / `task.payload.json` / `epic.payload.json` /
  `subtask.payload.json` — ADF payloads, ready for `acli jira workitem create --from-json`.
- `confluence-spec.md` — Confluence Spec/PRD template (Markdown, for `createConfluencePage` with
  `contentFormat: "markdown"`).
- `comments.md` — templated comments for an *existing* ticket (status update / QA verification /
  blocker / decision record).

**Wording rules — apply everywhere in this directory:** concise, plain, on-point.
- One idea per line. State the behavior, not a story. Numbers/IDs/paths over prose.
- No vague language: not "ใช้ไม่ได้" but *what* fails *when* (Atlassian bug-report guidance).
- If a section has nothing real to say, delete it — don't pad.
- Acceptance Criteria format/register/coverage rules → [`acceptance-criteria.md`](acceptance-criteria.md), not restated here.

---

## Bug/Story — two audiences, two templates each, by design

Bug and Story each have **two different templates for two different readers** — not duplicates,
don't try to collapse them:

- `bug.md` / `story.md` — Thai, PO/QA-facing, used by this skill's guided gather flow (Step 1–2).
- `bug.payload.json` / `story.payload.json` — dev-facing ADF payload, used for direct
  `--from-json` create when the content is already fully known (no guided gather needed).

Both share the same [Acceptance Criteria](acceptance-criteria.md) rule where the section applies.

## Task / Epic / Sub-task — payload only, no guided gather

These three have **only** a payload template (`task.payload.json`, `epic.payload.json`,
`subtask.payload.json`) — there's no Thai PO/QA guided flow for them. Fill the payload's
placeholders directly from what the user gave you, preview with `adf2md.py`, then create. Don't
invent a guided gather step that doesn't exist for these types.

```bash
acli jira workitem create --from-json "${CLAUDE_SKILL_DIR}/templates/task.payload.json"
```

Or write the body in Markdown (easier than editing ADF JSON) and convert first:
```bash
bash "${CLAUDE_SKILL_DIR}/scripts/md2adf.sh" mytask.md -s "Summary" -p TP -t Task > /tmp/wi.json
acli jira workitem create --from-json /tmp/wi.json
```

**Sections — required vs optional:**

### Bug — `bug.payload.json`

Derived from TP-418, 447, 455, 457, 460, 461.

| Section | When | Content (keep it concise) |
|---|---|---|
| สรุปปัญหา | always | 1–2 sentences: what broke / where / user impact |
| ขั้นตอน Reproduce | always | numbered actions, one step per line |
| ผลที่คาดหวัง | always | what should happen |
| ผลที่เกิดจริง | always | what happens + error/wrong state |
| ความรุนแรง | recommended | High/Medium/Low + one-line why |
| หลักฐาน | if available | env, account/order/id, screenshot/log |
| Technical Notes (dev) | if known | Root Cause / Fix / Files |

### Story — `story.payload.json`

User-centric work item. Derived from Atlassian [user stories guidance](https://www.atlassian.com/agile/project-management/user-stories) ("As a [user], I want [goal], so that [benefit]" — non-technical, end-user perspective).

| Section | When | Content |
|---|---|---|
| User Story | always | "As a <role>, I want <goal> so that <benefit>" |
| Context | always | background / why — 1–2 sentences, non-technical |
| Acceptance Criteria | always | see [acceptance-criteria.md](acceptance-criteria.md) |
| Technical Notes | if known | approach, constraints (delete if not yet known) |
| Dependencies | if known | blockers or things that must be waited on |
| References | if any | plan / Figma / PR / link |

### Task — `task.payload.json`

Implementation work. Derived from TP-466, 467, 473, 479.

| Section | When | Content |
|---|---|---|
| Context | always | why / goal, 1–2 sentences + plan link |
| Scope | always | files + what changes (line refs help) |
| Out of scope | recommended | what this task won't touch |
| Acceptance Criteria | always | see [acceptance-criteria.md](acceptance-criteria.md) |
| Tests | recommended | what to assert |
| References | if any | plan / Figma / PR links |

### Epic — `epic.payload.json`

High-level initiative that spans multiple sprints. Derived from Atlassian agile guidance ("large body of work, broken into smaller stories, scope flexes with feedback").

| Section | When | Content |
|---|---|---|
| Goal | always | business outcome / why this epic exists — 1–2 sentences |
| Scope | always | high-level what the epic covers (not file-level) |
| Out of scope | recommended | what the epic will not touch — prevents scope creep |
| Success Criteria | always | yes/no testable at epic level, one per line (epic-level, not the per-scenario GWT format — see note below) |
| Key Deliverables | always | milestones / shippable pieces (not a task list) |
| Dependencies & Risks | if known | blockers or things that must be waited on |
| Child Work Items | if known | task/story/sub-task breakdown (or delete if not yet planned) |
| References | if any | plan / PRD / Figma / link |

Epic's "Success Criteria" is deliberately a different concept from Bug/Story/Task/Sub-task's
"Acceptance Criteria" — epic-level outcomes aren't per-scenario GWT-shaped. Don't force it into
the AC format.

### Sub-task — `subtask.payload.json`

A slice of a parent. **Must have a parent** — sub-tasks cannot be top-level. Derived from TP-436, 437, 489.

| Section | When | Content |
|---|---|---|
| Scope | always | one clear action + files |
| Out of scope | recommended | what siblings handle (avoid overlap) |
| Acceptance Criteria | always | see [acceptance-criteria.md](acceptance-criteria.md) |
| Files affected | if known | paths touched |

Sub-task parent: set `parentIssueId` in the JSON (or `--parent <KEY>` on the CLI). `parentIssueId`
takes the issue **key** (e.g. `TP-479`) — verified by create+delete (sub-task created with
`parent = TP-479`, no numeric id needed).

---

## Confluence: Spec/PRD template

[`confluence-spec.md`](confluence-spec.md) — adapted from the Story template's DNA (business
reason → scope → requirements → decision points → references) but for a planning doc that covers
*multiple* requirements, each shaped as its own user story so it can be decomposed into separate
Jira Stories later (e.g. via `atlassian:spec-to-backlog`). Thai, same plain-language + GWT
Acceptance Criteria conventions as everywhere else in this directory.

⚠️ Same caveat as the comment templates: this is a **starting proposal**, adapted by request from
the Story template — not mined from real Confluence usage or confirmed as a Head-of-Engineering
standard. Revise once used in practice.

```bash
cat "${CLAUDE_SKILL_DIR}/templates/confluence-spec.md"   # fill in placeholders, then send via MCP:
```
```
mcp__plugin_atlassian_atlassian__createConfluencePage
  cloudId:    <resolved via getAccessibleAtlassianResources>
  spaceId:    <resolved via getConfluenceSpaces>
  title:      <spec title>
  body:       <filled-in template content>
  contentFormat: "markdown"
  contentType:   "page"
```

---

_Grounded in: real TP work items + Atlassian [bug-report template](https://www.atlassian.com/software/jira/templates/bug-report) / [user stories](https://www.atlassian.com/agile/project-management/user-stories) / [acceptance criteria](https://www.atlassian.com/work-management/project-management/acceptance-criteria) / [epics guidance](https://www.atlassian.com/agile/project-management/epics) + agile story/task/sub-task/epic breakdown best practices._
