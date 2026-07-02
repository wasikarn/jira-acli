---
name: acli
description: "Mechanical driver for the acli CLI — a backend tool, not a content-authoring skill (same role as the Atlassian MCP): search, view, edit, transition, comment, link, clone, bulk ops via JQL, Confluence/admin ops, auth, and ADF<->markdown conversion. Thai: 'ย้ายสถานะหลายตัว', 'export JQL', 'ย้าย ticket ไป Done'. For creating or editing the *content* of a Bug/Story/Task/Epic/Sub-task or a templated comment, use jira-acli:jira-content instead; for a Confluence page/spec/PRD, use jira-acli:confluence-content instead — each owns its product's template standard and calls into this skill's commands to execute. Use this skill directly only for mechanical/query/bulk/transition work with no template shape to get right. Don't use for non-Atlassian trackers or global CLI config."
---

# acli — Atlassian Cloud CLI

Drive Jira, Confluence, org admin, and Rovo Dev from the terminal. Auth-first, JQL-driven, confirmation-gated.

**Content creation/editing routes elsewhere** — `jira-acli:jira-content` (Jira Bug/Story/Task/Epic/Sub-task content) and `jira-acli:confluence-content` (Confluence Spec/PRD page content). They own the template standard and call into this skill's commands to execute. **Atlassian MCP is the fallback, not the default** — only for the closed list in [When acli can't](#when-acli-cant-fall-back-to-the-atlassian-mcp).

---

## Always first: auth gate

Two independent layers — global OAuth and per-product. A product can be authed even when the global profile is not. Check before any command.

```bash
acli jira auth status        # check BEFORE any jira command
acli confluence auth status
```

Not authed:
```bash
acli jira auth login --web                                              # OAuth, browser
echo "$TOKEN" | acli jira auth login --site SITE.atlassian.net --email me@x.com --token   # API token via stdin
```

> `--token` reads stdin only — never pass a token as a flag value. Token: https://id.atlassian.com/manage-profile/security/api-tokens

Full auth model + per-product details → `REFERENCE.md` § "Auth model".

## Core loop (Jira work items)

```bash
# 1. FIND — JQL is the selector for everything downstream
acli jira workitem search --jql "project = TEAM AND statusCategory != Done" --fields key,summary,status
acli jira workitem search --jql "..." --json     # parse | --csv export | --web open | --count | --paginate

# 2. INSPECT — ~80% fewer tokens than raw JSON:
acli jira workitem view KEY-123 --json | python3 ${CLAUDE_SKILL_DIR}/scripts/adf2md.py

# 3. CREATE — anything multi-section goes through md2adf.py (--description wraps plain text into ONE literal paragraph — see "Description format" below)
python3 ${CLAUDE_SKILL_DIR}/scripts/md2adf.py desc.md -s "Summary" -p TEAM -t Task > /tmp/wi.json && acli jira workitem create --from-json /tmp/wi.json
acli jira workitem create --summary "X" --project TEAM --type Task --assignee @me   # OK ONLY when there's no multi-section description
acli jira workitem create-bulk --from-csv issues.csv       # or --from-json; --generate-json scaffolds input

# 4. MUTATE — target by --key | --jql | --filter
acli jira workitem transition --key KEY-1 --list                          # discover valid statuses FIRST
acli jira workitem transition --jql "project = TEAM AND status = 'To Do'" --status "In Progress" --yes
acli jira workitem edit --key "KEY-1,KEY-2" --summary "..." --labels a,b
# ⚠️ edit --description REPLACES the whole description. Append safely: bash ${CLAUDE_SKILL_DIR}/scripts/acli-edit.sh KEY notes.md
# Templated comments (status update / QA / blocker / decision) route to jira-acli:jira-content.
python3 ${CLAUDE_SKILL_DIR}/scripts/md2adf.py note.md > /tmp/note.json && acli jira workitem comment create --key KEY-1 --body-file /tmp/note.json
acli jira workitem comment create --key KEY-1 --body "..."   # OK ONLY for a single plain sentence
# comment update needs --body-adf FILE (its --body/--body-file are plain-text-only, no ADF auto-detect):
acli jira workitem comment update --key KEY-1 --id 10001 --body-adf /tmp/note.json
acli jira workitem assign --key KEY-1 --assignee @me       # @me | default | email
```

`@me` self-assign, `default` project default. ⚠️ `assign --assignee` resolves `@me`/`default`/**email** only — a raw **accountId silently UNassigns** (acli prints "unassigned" and clears it; verified). For accountId / privacy-hidden emails → [When acli can't](#when-acli-cant-fall-back-to-the-atlassian-mcp). `--generate-json` scaffolds any complex create/edit/link input. Per-flag tables → `REFERENCE.md`.

**Description format:** Jira `description`/comment `body` is ADF. Flags (`--description`/`--body`) wrap plain text into **one literal ADF paragraph — no markdown parsing.** `## heading`, `**bold**`, numbered/bulleted lists typed straight into the flag show up in Jira as those literal characters, not formatting — this is the #1 cause of a ticket or comment rendering as garbled plaintext. Use the flag only for a single unformatted sentence. Anything with headings/lists/bold/multiple sections needs a real ADF object: write Markdown and run `python3 ${CLAUDE_SKILL_DIR}/scripts/md2adf.py desc.md` (bare doc mode — omit `-s/-p/-t` for a comment/append body). Read it back with `${CLAUDE_SKILL_DIR}/scripts/adf2md.py`. Attachment differs by command: `workitem create/edit` → `--from-json`; `comment create` → `--body`/`--body-file` (auto-detect plain vs. ADF); `comment update` → dedicated `--body-adf FILE` flag. Confluence body is storage-format XHTML. Rules + GOOD/BAD → `REFERENCE.md` "Description & body formats" + `examples/`. **Content standard (what a description/comment should say, AC format, etc.) is not this skill's concern** — that's `jira-acli:jira-content` § `templates/` (Jira) or `jira-acli:confluence-content` § `templates/` (Confluence).

## Bulk-mutation safety

Mutating bulk ops (`edit`, `transition`, `assign`, `delete`, `clone`, `link create`) accept `--jql`/`--filter` and a `--yes` confirmation skip.

1. **Preview the set first** — run `search` with the *exact same* `--jql` and `--count` before any `--yes` mutation. The JQL selects what you'll change; verify it.
2. `--yes` skips the interactive confirm — only after the preview matches intent.
3. `--ignore-errors` continues past per-item failures. Default OFF — read the result summary; a partial failure must be loud, not swallowed. Sub-tasks can't be archived/deleted on their own (✗ "Issue is a subtask"), so a key-list `archive`/`delete` batch reports partial failures — archive/transition the parent or the sub-tasks separately.

## Create safety

`create`/`create-bulk` are outward-facing too — but unlike the mutations above they have no JQL set to preview, so preview the **payload itself** before firing.

1. **Render what you're about to send.** For a `--from-json` create, round-trip it first: `python3 ${CLAUDE_SKILL_DIR}/scripts/md2adf.py desc.md -s "..." -p TP -t Bug > /tmp/wi.json && python3 ${CLAUDE_SKILL_DIR}/scripts/adf2md.py /tmp/wi.json` prints a readable card — `(new) <type>`, project, labels, and the full description. Eyeball it, *then* `acli jira workitem create --from-json /tmp/wi.json`.
2. For `create-bulk`, `--generate-json` first (or render one row) and read it back before the batch — a bad template multiplies across every row. ⚠️ `create-bulk --from-json` **rejects rich-markdown descriptions** (headings/code fences/backticks/newlines) → ✗ "request body is missing or invalid". Pattern that works: bulk-create with **short placeholder** bodies, then set the real description per ticket with `bash ${CLAUDE_SKILL_DIR}/scripts/acli-set-desc.sh KEY desc.md` (verified TP-558..566).
3. **Resolve metadata, don't hardcode it.** Project/type/priority/labels/assignee must match the target project; `--generate-json` emits the schema the project actually accepts — scaffold from it when unsure of a type or field. The templates ship `projectKey:"TP"` as a personal default — swap it (or pass `-p`) for any other project. On an unknown project/type/field acli fails: fix it, never strip the field and retry.

## Confluence / admin / rovodev

```bash
acli confluence page view --id 123 --body-format storage   # page is view-only — create/update needs MCP, see below
acli confluence blog create --space-id 12345 --title "T" --body "<p>storage-format XHTML</p>"
acli confluence space create --key KEY --name "Name"       # space: full CRUD
acli admin user deactivate ...                             # org user lifecycle (admin auth)
acli rovodev auth login && acli rovodev run                # AI coding agent (beta, separate token)
```

Full command tree, every flag, and JSON schemas → `REFERENCE.md`.

## Confluence & admin write safety

`confluence blog create`, `confluence space create`, and every `admin user` lifecycle command (`activate`/`deactivate`/`delete`/`cancel-delete`) have **no native `--yes`/confirm flag** — unlike `jira workitem edit/transition/assign`, nothing in acli itself stops a bad target from firing. This skill supplies the safety net manually:

1. **Confluence blog/space create** — same rule as [Create safety](#create-safety) above: no JQL set to preview, so preview the **payload** instead. Render the body/title/space before sending; for `--from-file`/`--from-json`, read the file back and eyeball it first.
2. **`admin user` lifecycle ops are the highest blast-radius command in this plugin** — deactivate/delete act on real accounts, `--from-file` accepts a bulk target list, and `--ignore-errors` continues past per-account failures with none of it caught by acli itself. Before running any `admin user deactivate|delete|cancel-delete`:
   - Resolve and print the **exact target list** (emails/accountIds) and get explicit user go-ahead — the missing native confirm flag is this skill's job to backfill, not a license to skip confirmation.
   - Leave `--ignore-errors` off by default, same as [Bulk-mutation safety](#bulk-mutation-safety) — a partial failure across accounts must be loud, not swallowed.
   - `activate`/`cancel-delete` are recoverable; `deactivate`/`delete` are not (or not cheaply) — weight the confirmation ask accordingly.

## When acli can't (fall back to the Atlassian MCP)

acli is the default. A small, closed set of operations genuinely need `mcp__plugin_atlassian_atlassian__*` (or the Jira UI) — this list is the full accounting, not a sample. If you're about to name an MCP tool anywhere in this plugin for something not on this list, check `REFERENCE.md`'s command surface first and add the row here if it's genuine, don't let it live undocumented in `jira-content`/`confluence-content`. Reach for the MCP **only** here:

- **Set/​change parent on an *existing* issue** — `edit --from-json` has no parent field and rejects a `parent` key; `--parent`/`parentIssueId` work only at *create* time (sub-tasks). → MCP `editJiraIssue cloudId:<id> issueIdOrKey:"TP-NNN" fields:{parent:{key:"TP-505"}}`.
- **Assign by accountId** when the email is privacy-hidden (`--assignee email` can't resolve, and a raw accountId silently UNassigns). → MCP `editJiraIssue cloudId:<id> issueIdOrKey:"TP-NNN" fields:{assignee:{accountId:"…"}}`; resolve the id with `lookupJiraAccountId cloudId:<id> searchString:"<name|email>"`.
- **fixVersion / release versions** — acli has no `version create`, `edit --from-json` rejects `fixVersions`, and `search --fields fixVersions` errors (read it via `view --json` + parse). → MCP or the Jira UI.
- **Issue-type metadata for a project** — no acli command exposes which fields/issue-types a project accepts at create time (`jira field` only manages custom fields; `create --generate-json`'s schema doesn't vary by project/type). → MCP `getJiraProjectIssueTypesMetadata cloudId:<id> projectIdOrKey:"TP"` (singular — one project per call) to list issue types, then `getJiraIssueTypeMetaWithFields cloudId:<id> projectIdOrKey:"TP" issueTypeId:"<id>"` for that type's actual field list, when a create rejects and you need to confirm why.
- **Priority / Environment / Affects-Version at *create* time** — none of these three appear in `create --generate-json`'s schema or `--help` output, for any project/type (verified empirically). → set via MCP `createJiraIssue`'s `additional_fields` — see `jira-acli:jira-content` § Step 5b.
- **cloudId** — acli has no cloudId concept at all; it operates against the currently authed site transparently. Every MCP call above needs one. → MCP `getAccessibleAtlassianResources`. Not a capability gap of its own — a prerequisite lookup for every other row here.
- **Create/update a Confluence *page*** — acli `confluence page view` covers reads (including via `--body-format atlas_doc_format` + `${CLAUDE_SKILL_DIR}/scripts/adf2md.py`), but **writes are genuinely MCP-only** (blog + space have full CRUD, page does not). → MCP `createConfluencePage` / `updateConfluencePage`. ⚠️ These take `contentFormat: "html"|"markdown"|"adf"` — a **different content model from `acli confluence blog create`'s storage-format XHTML.** For a plain doc (headings/lists/bold, no Confluence-specific panels/macros) pass `contentFormat: "markdown"` with a raw Markdown body — don't hand-write XHTML for a page, that's the blog-only mechanism. Spec/PRD template → `jira-acli:confluence-content` § `templates/confluence-spec.md`.
- **Move an issue to a different project** — the one row here with **no MCP fallback either.** `edit --from-json` has no project-move field, and Jira Cloud doesn't expose a project move via the plain edit endpoint — it requires the separate [Bulk Move REST API](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-bulk-operations/) (beta), which none of the Atlassian MCP tools available in this plugin wrap. → Jira UI's bulk-move wizard only. Don't attempt this via `editJiraIssue`'s `fields:{project:{...}}` — it isn't a supported path.

## METHODOLOGY

- **Rule 1 (think before coding):** auth-status + JQL-preview before any bulk mutation — `--yes` on a wrong JQL is silent orthogonal damage at scale.
- **Code for judgment:** let JQL deterministically select work items; don't hand-enumerate keys you could query.
- **Fail loud:** `--ignore-errors` off by default; "transitioned 40" must not hide "skipped 12". On a *single* create/edit rejected for an unknown field/label/type, report the exact error — never silently drop the offending field and retry. A dropped field is a silent spec change.

## Related

- `jira-acli:jira-content` — Jira Bug/Story/Task/Epic/Sub-task content and templated comments. Calls into this skill to execute.
- `jira-acli:confluence-content` — Confluence Spec/PRD page content. Calls into the Atlassian MCP directly (no acli path for page create/update).
- Atlassian MCP (`mcp__plugin_atlassian_atlassian__*`) — fallback only, for the acli gaps in [When acli can't](#when-acli-cant-fall-back-to-the-atlassian-mcp); not the default for single ops. Provided by the official Atlassian plugin — install that plugin for the fallback to resolve.
