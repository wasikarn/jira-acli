> **Content templates live in `jira-acli:jira-content` § `templates/` (Bug/Story/Task/Epic/
> Sub-task, comments) and `jira-acli:confluence-content` § `templates/` (Confluence Spec/PRD).**
> This directory is the acli **mechanics** reference —
> ADF/XHTML shape, the `--from-json` vs flag distinction, and the two different Confluence content
> models. It has no opinion on what a ticket's content should say.

# acli examples — description & body formats

GOOD/BAD reference for the #1 acli pitfall: **Jira uses ADF, `--from-json` is stricter than the flags, and Confluence's content format depends on which command you're using — `acli confluence blog create` wants storage XHTML, but Confluence *page* create/update (MCP-only — acli's `page` command is view-only) accepts `html`/`markdown`/`adf` via `contentFormat`.** Each pair shows WHY, not just WHAT.

Files here:

- `workitem-from-json.good.json` — valid `create-bulk --from-json` input (ADF description)
- `workitem-from-json.bad.json` — same intent, wrong description shape (do **not** use)

---

## 1. Jira description via `--from-json`

`description` must be a full ADF document object — a bare string does not match the schema.

**GOOD** (`workitem-from-json.good.json`):
```json
"description": { "type": "doc", "version": 1,
  "content": [ { "type": "paragraph",
    "content": [ { "type": "text", "text": "Repro steps: ..." } ] } ] }
```

**BAD** (`workitem-from-json.bad.json`):
```json
"description": "Repro steps: ..."
```
Why: the generated schema (`acli jira workitem create --generate-json`) emits `description` as an ADF `{type:"doc",...}` object. A plain string is not ADF, so it won't be accepted/rendered as intended.

---

## 2. Jira description via flag — plain text is fine

The flag path wraps plain text into ADF for you. Do **not** hand-write ADF JSON on the command line.

**GOOD:**
```bash
acli jira workitem create -p TEAM -t Task -s "Login bug" \
  --description "Users hit a 500 on submit. Repro: POST /login with empty body."
```

**BAD:**
```bash
acli jira workitem create -p TEAM -t Task -s "Login bug" \
  --description '{"type":"doc","version":1,"content":[...]}'
```
Why: the flag already accepts plain text and wraps it. Pasting raw ADF JSON as a flag value is redundant and error-prone (shell quoting, escaping). Reserve ADF objects for `--from-json`.

---

## 3. Don't mix Jira ADF with Confluence storage format

**BAD — Confluence XHTML in a Jira description:**
```bash
acli jira workitem create -p TEAM -t Task -s "X" --description "<p>Hello</p>"
```
Why: `<p>...</p>` is Confluence **storage format**, not Jira ADF. In Jira the tags show as literal text — Jira does not parse XHTML.

**BAD — Markdown expecting render:**
```bash
acli jira workitem create -p TEAM -t Task -s "X" --description "See **the docs**"
```
Why: ADF `text` nodes are literal. `**the docs**` renders as the literal asterisks, not bold. Use the flag's plain text for plain text; build an ADF object with marks if you need bold/links.

---

## 4. Confluence body — two different mechanisms, don't conflate them

**`acli confluence blog create` (acli, blogs only) wants storage-format XHTML:**

**GOOD:**
```bash
acli confluence blog create --space-id 12345 --title "Release Notes" \
  --body "<p>Shipped <strong>v2</strong>. <a href=\"https://x\">Changelog</a>.</p>"
```

**BAD — ADF JSON into Confluence:**
```bash
acli confluence blog create --space-id 12345 --title "X" \
  --body '{"type":"doc","version":1,...}'
```
Why: Confluence's storage format is XHTML, the inverse of Jira. ADF here renders as literal JSON text.

**`createConfluencePage`/`updateConfluencePage` (MCP, the only way to create/update a *page* — acli's `confluence page` is view-only) is a different content model entirely:** `contentFormat` is `"html"` (Confluence's own HTML+ dialect — `data-type` attributes for panels/status/task-lists/etc., NOT the same thing as `blog create`'s storage XHTML), `"markdown"`, or `"adf"`. For a plain document with headings/lists/bold — no Confluence-specific panels/macros — pass `contentFormat: "markdown"` and the raw Markdown body directly; skip hand-authoring HTML or ADF entirely. Template for this → `jira-acli:confluence-content` § `templates/confluence-spec.md`.

---

## Quick rule

| You're writing... | Use |
|---|---|
| Jira, via flag | plain text (auto-wrapped to ADF) |
| Jira, via `--from-json` | ADF `{type:"doc",version:1,content:[...]}` object |
| Confluence, via `acli confluence blog create` | storage format XHTML (`<p>`, `<strong>`, `<a>`) |
| Confluence page, via MCP `createConfluencePage`/`updateConfluencePage` | `contentFormat: "markdown"` + plain Markdown body (or `"html"`/`"adf"` for richer Confluence-specific elements) |

Regenerate the canonical schema any time with `acli jira workitem create --generate-json`.
