# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A **Claude Code plugin**, not an application. It ships two skills (`skills/acli`, `skills/create-jira-ticket`) — markdown instruction files plus small Python/Bash helper scripts — that teach Claude to drive Jira/Confluence through the `acli` CLI, falling back to the official Atlassian MCP plugin only where `acli` genuinely can't do something. There is no server, no package manifest, and no runtime beyond `python3`/`bash` + the user's own `acli` install.

## Commands

There is no build step, package manager, or test framework in this repo. The only useful local checks:

```bash
# Syntax-check every helper script (fast, no deps)
python3 -m py_compile skills/*/scripts/*.py
for f in skills/*/scripts/*.sh; do bash -n "$f"; done
shellcheck skills/*/scripts/*.sh   # if installed

# Exercise a converter directly (round-trip check)
python3 skills/acli/scripts/md2adf.py somefile.md | python3 skills/acli/scripts/adf2md.py -
```

No `run-tests.sh` exists in this repo despite one comment in `md2adf.py` referencing it (a holdover from the parent `kbg-harness` project this was extracted from) — don't assume a test suite exists.

**Releasing:** bump `version` in **both** `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` on every change — Claude Code treats a same-version edit to an already-cached plugin as a silent no-op, so a bump is required even for doc-only fixes.

## Architecture

### Plugin structure

`.claude-plugin/plugin.json` + `marketplace.json` declare the plugin; `defaultEnabled: false` means installers must opt in via `settings.json`. Everything else lives under `skills/<name>/`, each with a required `SKILL.md` (frontmatter `name` + `description` is what triggers auto-invocation) plus `scripts/` and/or `references/` loaded on demand.

### The two skills, and why they're split

- **`acli`** — the default surface for *everything* Jira/Confluence: search, view, edit, transition, comment, bulk ops, Confluence/admin. Model-invokable with no confirmation gate at the skill level because every mutating command is itself confirmation-gated (JQL preview before `--yes`, payload preview before create).
- **`create-jira-ticket`** — guided creation of a *single* Bug/Story using a Thai PO/QA template, with its own preview-and-confirm gate. It depends on `acli`'s `md2adf.py` (via its own `scripts/md2adf.sh` wrapper) — the two skills are not separable; changes to the ADF schema in one must be checked against the other.

Routing between them (and to the Atlassian MCP fallback) is doctrine encoded in each `SKILL.md`'s frontmatter `description` and body — read those before changing behavior, since they're what the model uses to decide which skill fires.

### ADF ⟷ Markdown conversion (the core data-flow)

Jira descriptions/comments are Atlassian Document Format (ADF) JSON; Confluence bodies are storage-format XHTML. Hand-writing ADF is error-prone, so everything routes through:

- **`skills/acli/scripts/md2adf.py`** — parses a small Markdown subset (headings, ordered/bullet/task lists, bold/italic/code/strike/links, code blocks, blockquotes, rules) into an ADF doc, or a full `acli ... create --from-json` payload when `-s/-p/-t` are passed. Nested lists are *deliberately* flattened (see `skills/acli/ISSUES.md` Issue 1) — the documented workaround is H3 sub-headings + flat bullets, not a bug to fix.
- **`skills/acli/scripts/adf2md.py`** — the inverse: renders raw ADF, a full `workitem view --json` payload, or a bare create-payload (flat keys, no `fields` wrapper — see `render_create_card`) back to readable Markdown. Handles the acli list-or-dict shape drift across versions.
- **`skills/acli/scripts/acli-edit.py`** — read-modify-write for descriptions (append / remove-section / replace-section by heading), since `acli edit --description` replaces the whole body. Section boundaries are found by heading level, not string matching.
- **`skills/acli/scripts/acli-ls.py`** — normalizes `workitem search --json` (list-or-dict, nested-field-or-null) into an aligned table; exists because this exact shape was reinvented 40+ times in practice.

Every `.sh` wrapper in `skills/acli/scripts/` resolves its own path via `BASH_SOURCE[0]` so a skill body can call it as `${CLAUDE_SKILL_DIR}/scripts/foo.sh` regardless of where the plugin is installed — preserve that pattern in any new wrapper rather than hardcoding paths. `skills/create-jira-ticket/scripts/md2adf.sh` is a thin cross-skill wrapper that walks back up to `skills/acli/scripts/md2adf.py` for exactly this reason.

### Conventions specific to this codebase

- **Fail loud, never silently drop a field.** Every script here exits non-zero with a `FATAL:` message on bad input rather than guessing or dropping data — an unknown Jira field/label/type must surface as an error, not get silently stripped and retried (see `acli/SKILL.md` METHODOLOGY).
- **Preview before mutate.** Bulk mutations preview via the same `--jql`; creates preview via rendering the payload with `adf2md.py` before firing. This is load-bearing UX, not incidental — replicate it in any new script that writes to Jira/Confluence.
- **acli is the default, Atlassian MCP is the fallback**, used only for the ~4 documented gaps (`acli/SKILL.md` § "When acli can't"): parent-reassignment on an existing issue, assign-by-accountId, fixVersions, and Confluence *page* create/update. Don't reach for MCP tools outside that list without updating the doc.
- **Acceptance-criteria wording rules are canonical in one place** — `skills/acli/examples/README.md` — and referenced, not duplicated, from `create-jira-ticket`'s references and `SKILL.md`. If you change the AC rubric, edit it there.
