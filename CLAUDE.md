# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A **Claude Code plugin**, not an application. It ships two skills (`skills/acli`, `skills/jira-content`) — markdown instruction files plus small Python/Bash helper scripts — that teach Claude to drive Jira/Confluence through the `acli` CLI, falling back to the official Atlassian MCP plugin only where `acli` genuinely can't do something. There is no server, no package manifest, and no runtime beyond `python3`/`bash` + the user's own `acli` install.

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

### The two skills, and why they're split: tool vs. content

The split is **mechanics vs. content**, not "broad vs. guided" — `acli` is a backend tool (the
same role as the Atlassian MCP), `jira-content` is the layer that decides what a ticket/page/
comment's body should actually say.

- **`acli`** — pure tool/mechanics for *everything* Jira/Confluence: search, view, edit metadata,
  transition, comment plumbing, bulk ops, Confluence/admin, auth, ADF↔Markdown conversion. It has
  no opinion on ticket content or format — it just executes. Model-invokable with no confirmation
  gate at the skill level because every mutating command is itself confirmation-gated (JQL preview
  before `--yes`, payload preview before create).
- **`jira-content`** — owns the team's template standard and decides *what goes in the body*:
  guided creation of Bug/Story (Thai PO/QA template), payload-driven creation of Task/Epic/
  Sub-task, Confluence Spec/PRD pages, templated comments, and template-conforming edits. All
  templates live under `skills/jira-content/templates/` — the single source of truth (see
  `templates/README.md` and `templates/acceptance-criteria.md`). It has its own preview-and-confirm
  gate, and calls into `acli`'s commands (via a thin cross-skill wrapper, same pattern as
  `md2adf.sh`) to actually execute the write.

The two skills are not separable — `jira-content`'s wrapper scripts (`scripts/md2adf.sh`,
`scripts/acli-edit.sh`, `scripts/acli-set-desc.sh`) all delegate to `acli`'s Python scripts;
changes to the ADF schema or script interface in `acli` must be checked against `jira-content`.

Routing between them (and to the Atlassian MCP fallback) is doctrine encoded in each `SKILL.md`'s
frontmatter `description` and body — read those before changing behavior, since they're what the
model uses to decide which skill fires. Every new skill boundary is a routing-failure surface (a
contradictory or overlapping `description` is exactly how tickets ended up bypassing these skills
entirely in the past) — keep the boundary crisp: "shapes content to a template" → `jira-content`;
everything else → `acli`.

### ADF ⟷ Markdown conversion (the core data-flow)

Jira descriptions/comments are Atlassian Document Format (ADF) JSON; Confluence bodies are storage-format XHTML. Hand-writing ADF is error-prone, so everything routes through:

- **`skills/acli/scripts/md2adf.py`** — parses a small Markdown subset (headings, ordered/bullet/task lists, bold/italic/code/strike/links, code blocks, blockquotes, rules) into an ADF doc, or a full `acli ... create --from-json` payload when `-s/-p/-t` are passed. Nested lists are *deliberately* flattened (see `skills/acli/ISSUES.md` Issue 1) — the documented workaround is H3 sub-headings + flat bullets, not a bug to fix.
- **`skills/acli/scripts/adf2md.py`** — the inverse: renders raw ADF, a full `workitem view --json` payload, or a bare create-payload (flat keys, no `fields` wrapper — see `render_create_card`) back to readable Markdown. Handles the acli list-or-dict shape drift across versions.
- **`skills/acli/scripts/acli-edit.py`** — read-modify-write for descriptions (append / remove-section / replace-section by heading), since `acli edit --description` replaces the whole body. Section boundaries are found by heading level, not string matching.
- **`skills/acli/scripts/acli-ls.py`** — normalizes `workitem search --json` (list-or-dict, nested-field-or-null) into an aligned table; exists because this exact shape was reinvented 40+ times in practice.

Every `.sh` wrapper in `skills/acli/scripts/` resolves its own path via `BASH_SOURCE[0]` so a skill body can call it as `${CLAUDE_SKILL_DIR}/scripts/foo.sh` regardless of where the plugin is installed — preserve that pattern in any new wrapper rather than hardcoding paths. `skills/jira-content/scripts/{md2adf,acli-edit,acli-set-desc}.sh` are thin cross-skill wrappers that walk back up to the matching script under `skills/acli/scripts/` for exactly this reason — same idiom, `../../..` climb to the plugin root then back down.

### Conventions specific to this codebase

- **Fail loud, never silently drop a field.** Every script here exits non-zero with a `FATAL:` message on bad input rather than guessing or dropping data — an unknown Jira field/label/type must surface as an error, not get silently stripped and retried (see `acli/SKILL.md` METHODOLOGY).
- **Preview before mutate.** Bulk mutations preview via the same `--jql`; creates preview via rendering the payload with `adf2md.py` before firing. This is load-bearing UX, not incidental — replicate it in any new script that writes to Jira/Confluence.
- **acli is the default, Atlassian MCP is the fallback**, used only for the ~4 documented gaps (`acli/SKILL.md` § "When acli can't"): parent-reassignment on an existing issue, assign-by-accountId, fixVersions, and Confluence *page* create/update. Don't reach for MCP tools outside that list without updating the doc.
- **All content templates are canonical in one place** — `skills/jira-content/templates/` — and referenced, not duplicated, from every skill/doc that needs them. Acceptance Criteria format/register/coverage rules specifically live in `templates/acceptance-criteria.md`; every other file (Bug/Story/Task/Epic/Sub-task templates, the Confluence Spec/PRD template, comment templates) points there instead of restating the rule. If you change the AC rubric or any template, edit it there — this consolidation exists because the old scattered-copies setup let the AC format drift out of sync across 5+ files in practice.
