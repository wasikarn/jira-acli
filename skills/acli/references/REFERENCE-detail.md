# acli Reference — Per-flag recipes

Loaded on demand. Core command tables + format overview live in
[`../REFERENCE.md`](../REFERENCE.md); routing + safety in [`../SKILL.md`](../SKILL.md).

## jira workitem — per-flag enumerations

### create

`-s/--summary`, `-p/--project`, `-t/--type` (Epic/Story/Task/Bug…), `-a/--assignee` (`@me`|`default`|email), `-d/--description` (plain or ADF), `--description-file`, `-l/--label`, `--parent`, `-e/--editor`, `-f/--from-file`, `--from-json`, `--generate-json`, `--json`.

### create-bulk

`--from-csv`, `--from-json`, `--generate-json`, `--ignore-errors`, `--yes`.

### search

`-j/--jql`, `--filter`, `-f/--fields` (default `issuetype,key,assignee,priority,status,summary`), `-l/--limit`, `--paginate`, `--count`, `--json`, `--csv`, `-w/--web`.

### view

`-f/--fields` accepts `*all`, `*navigable`, `field,field`, or `-field` to exclude (default `key,issuetype,summary,status,assignee,description`). `--json`, `-w/--web`.

### edit

`-k/--key`, `--jql`, `--filter`, `-s/--summary`, `-d/--description`, `--description-file`, `-t/--type`, `-a/--assignee`, `--remove-assignee`, `-l/--labels`, `--remove-labels`, `--from-json`, `--generate-json`, `--ignore-errors`, `-y/--yes`, `--json`.

### transition

`-k/--key`, `--jql`, `--filter`, `-s/--status`, `--ignore-errors`, `-y/--yes`, `--json`. No `--list` — removed in current acli (confirmed gone in `1.3.22-stable`); see `../SKILL.md` § "When acli can't" for read-only transition discovery via MCP.

### assign

`-k/--key`, `--jql`, `--filter`, `-f/--from-file`, `-a/--assignee`, `--remove-assignee`, `--ignore-errors`, `-y/--yes`, `--json`.

### comment

`create` flags: `-b/--body` (plain text OR a raw ADF string — auto-detected), `-F/--body-file` (same, but a file), `-e/--edit-last`, `--editor`, selectors, `--ignore-errors`, `--json`. `comment list|delete|visibility` for the rest of the lifecycle.

### link

`create` flags: `--out`, `--in`, `--type` (outward description, e.g. Blocks), `--from-json`, `--from-csv` (out,in,type; header row ignored), `--generate-json`, `--ignore-errors`, `--yes`.

### clone

`-k/--key`, `--jql`, `--filter`, `-f/--from-file`, `--to-project`, `--to-site` (default = current authed site), `--ignore-errors`, `-y/--yes`, `--json`.

### project create

Clone-only (`--from-project`, company-managed only) or `--from-json`; flags `-k/--key`, `-n/--name`, `-d/--description`, `-u/--url`, `-l/--lead-email`. `sprint create` requires `--name` + `--board`; dates ISO 8601.

### confluence space

`list`: `--keys` (comma-separated — ⚠️ accepted but does NOT filter, confirmed live 2026-08-04; always returns the full space list regardless, match `key` client-side instead of trusting the response order), `--type` (global|personal), `--status` (current|archived, default current), `--expand` (description,homepage,permissions), `-l/--limit` (default 50), `--json`. `create`: `--key`, `--name`, `--description`, `--private`, `--alias`, `--template-key`, `--json`. `archive`/`restore`: `--key` only. `update`: `--key`, `--name`, `--description`, `--status`, `--type`, `--json`. `view`: `--id` (not `--key` — see `../REFERENCE.md` § confluence/admin), plus `--icon`, `--labels`, `--operations`, `--permissions`, `--properties`, `--role-assignments` (EAP only), `--include-all`, `--desc-format` (plain|view), `--json`. Verified live against `1.3.22-stable`, 2026-07-24 (space CRUD) / 2026-08-04 (`--keys` filter behavior).

### confluence blog create

`--space-id`, `--title`, `--body`, `--status` (current|draft, default current), `--private`, `--created-at` (ISO 8601), `--from-file`, `--from-json`, `--generate-json`, `-j/--json`.

### confluence page view

`--body-format storage|atlas_doc_format|view`. Include flags: `--include-labels`, `--include-version`, `--include-direct-children`, `--include-properties`, `--status current,draft,archived`, `--version N`, `--get-draft`.

## Edit: manual read-modify-write (surgical in-place edits)

For edits the one-step helpers (`acli-edit.sh` append/remove-section/
replace-section) don't cover — e.g. multiple section changes in one round-trip,
or moving a section's position.

```bash
acli jira workitem view KEY --fields description --json   # grab .fields.description (ADF)
#   …edit the content[] array (append/replace/remove nodes)…
acli jira workitem edit --from-json payload.json          # { "issues": ["KEY"], "description": <merged ADF> }
```

Section boundaries in `acli-edit.sh` are found by heading level, not string
matching — re-use that approach when hand-editing ADF (`content[]` nodes of
`type: "heading"` delimit a section).

## Output & scripting cheatsheet

| Need | Flag |
|---|---|
| Machine-parseable | `--json` |
| Spreadsheet export | `--csv` (search) |
| Open in browser | `-w/--web` |
| Count only | `--count` (search) |
| All results | `--paginate` (search) |
| Scaffold input file | `--generate-json` (create/edit/link/bulk/project/blog) |
| Skip confirm prompt | `-y/--yes` (mutating bulk ops) |
| Continue past failures | `--ignore-errors` (read the summary after!) |
| Read body/desc from file | `--from-file` / `--body-file` / `--description-file` |
| Markdown → ADF for `--from-json` | `python3 ${CLAUDE_SKILL_DIR}/scripts/md2adf.py desc.md` |
| Read a work item cheaply (ADF → md) | `acli ... view KEY --json \| python3 ${CLAUDE_SKILL_DIR}/scripts/adf2md.py` (~80% fewer tokens) |
| Create from Markdown in one step | `bash ${CLAUDE_SKILL_DIR}/scripts/acli-new.sh desc.md -s "..." -p TP -t Bug` |
| Append to a description (no loss) | `bash ${CLAUDE_SKILL_DIR}/scripts/acli-edit.sh KEY notes.md` |
| Remove a description section | `bash ${CLAUDE_SKILL_DIR}/scripts/acli-edit.sh KEY --remove-section "HEADING"` |
| Replace a section in place | `bash ${CLAUDE_SKILL_DIR}/scripts/acli-edit.sh KEY --replace-section "HEADING" new.md` |
| **Replace** the whole description from Markdown | `bash ${CLAUDE_SKILL_DIR}/scripts/acli-set-desc.sh KEY desc.md [--dry-run]` (overwrites; for the bulk placeholder→body flow) |
| List a JQL/key set as a table | `bash ${CLAUDE_SKILL_DIR}/scripts/acli-ls.sh --jql "project = TP AND statusCategory != Done"` (or `--key TP-1,TP-2`) |
| Render a set as readable cards | loop `view KEY --json \| python3 ${CLAUDE_SKILL_DIR}/scripts/adf2md.py` (adf2md also accepts a JSON array) |
| Relate N items in one shot | `acli jira workitem link create --from-csv links.csv` (header `out,in,type`) |

ADF = Atlassian Document Format (Jira rich text); storage format = Confluence XHTML. Full rules + GOOD/BAD inputs: see `../REFERENCE.md` § "Description & body formats" + `examples/`.
