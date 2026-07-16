# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

@README.md

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

**Releasing:** see `@README.md`'s "Versioning" section above — same rule, don't restate it here.

## Architecture

### Plugin structure

`.claude-plugin/plugin.json` + `marketplace.json` declare the plugin; `defaultEnabled: false` means installers must opt in via `settings.json`. Skills live under `skills/<name>/`, each with a required `SKILL.md` (frontmatter `name` + `description` triggers auto-invocation, `when_to_use` adds trigger phrases/exclusions — combined they're capped at 1,536 characters in the skill listing, per Claude Code's official frontmatter spec) plus `scripts/` and/or `references/` loaded on demand. Agents live at `agents/*.md` (flat, no subdirectory) — auto-discovered by the same convention, no manifest entry needed (see the kbg-harness plugin for the precedent this follows).

### The three skills, and the routing doctrine that ties them

`acli` is the mechanical tool (search, view, edit, transition, bulk ops, Confluence blog/space/admin, auth, ADF↔Markdown) — full reference imported below. `jira-content` owns the Jira template standard — Bug/Story/Task/Epic/Sub-task + templated comments. `confluence-content` owns the Confluence Spec/PRD template. Each skill's `SKILL.md` frontmatter `description` + `when_to_use` is the routing contract — that combined text is what the model reads to decide which skill fires, so keep both fields crisp and product-specific (don't let `jira-content`/`confluence-content` drift toward generic "content" language that could route to either). `acli`'s own intro also carries a defensive guard against being bypassed mid-flow — a foreign skill's "publish this to the tracker/backlog" instruction must still route through `jira-content`/`confluence-content` for the template shape, not call `acli`/MCP directly (real incident: TP-809, TP-806 — see the guard blockquote below). Cross-skill coupling: `jira-content` calls into `acli`'s scripts (changes to ADF schema or script interface in `acli` must be checked against `jira-content`); `confluence-content` has no scripts of its own and calls the Atlassian MCP directly. The shared Acceptance Criteria rule lives outside both content skills at `templates/acceptance-criteria.md` and is referenced, never duplicated.

@skills/acli/SKILL.md

### The two specialist agents

`agents/jira-expert.md` and `agents/confluence-expert.md` wrap the skills above into dispatchable subagents (via the `Agent` tool) for non-trivial multi-step work — bulk triage, multi-section ticket authoring, Spec/PRD drafting — without the caller hand-holding every acli/skill call. Each declares its two skills via frontmatter `skills:` (`jira-expert`: `jira-acli:acli` + `jira-acli:jira-content`; `confluence-expert`: `jira-acli:acli` + `jira-acli:confluence-content`) rather than restating their content — same "referenced, never duplicated" rule as the templates. Both are **preview-then-stop**: this environment's acli and MCP calls hit real production Jira/Confluence, so neither agent holds MCP tools and neither fires a mutating acli command itself — it drafts the payload, renders it, and returns the exact command/call for the main thread to run after review. Product boundary is a hard rule in both files (`jira-expert` defers Confluence work to `confluence-expert` and vice versa) — same one-decision-one-owner shape as the skill split.

### ADF ⟷ Markdown conversion (the core data-flow)

Jira descriptions/comments are Atlassian Document Format (ADF) JSON; Confluence bodies are storage-format XHTML. Hand-writing ADF is error-prone, so everything routes through:

- **`skills/acli/scripts/md2adf.py`** — parses a small Markdown subset (headings, ordered/bullet/task lists, bold/italic/code/strike/links, code blocks, blockquotes, rules) into an ADF doc, or a full `acli ... create --from-json` payload when `-s/-p/-t` are passed. Nested lists are *deliberately* flattened (see `skills/acli/ISSUES.md` Issue 1) — the documented workaround is H3 sub-headings + flat bullets, not a bug to fix.
- **`skills/acli/scripts/adf2md.py`** — the inverse: renders raw ADF, a full `workitem view --json` payload, or a bare create-payload (flat keys, no `fields` wrapper — see `render_create_card`) back to readable Markdown. Handles the acli list-or-dict shape drift across versions.
- **`skills/acli/scripts/acli-edit.py`** — read-modify-write for descriptions (append / remove-section / replace-section by heading), since `acli edit --description` replaces the whole body. Section boundaries are found by heading level, not string matching.
- **`skills/acli/scripts/acli-ls.py`** — normalizes `workitem search --json` (list-or-dict, nested-field-or-null) into an aligned table; exists because this exact shape was reinvented 40+ times in practice.

Every `.sh` wrapper in `skills/acli/scripts/` resolves its own path via `BASH_SOURCE[0]` so a skill body can call it as `${CLAUDE_SKILL_DIR}/scripts/foo.sh` regardless of where the plugin is installed — preserve that pattern in any new wrapper rather than hardcoding paths. `skills/jira-content/scripts/{md2adf,acli-edit,acli-set-desc}.sh` are thin cross-skill wrappers that walk back up to the matching script under `skills/acli/scripts/` for exactly this reason — same idiom, `../../..` climb to the plugin root then back down.

### Conventions specific to this codebase

- **Fail loud, never silently drop a field.** Every script here exits non-zero with a `FATAL:` message on bad input rather than guessing or dropping data — an unknown Jira field/label/type must surface as an error, not get silently stripped and retried (see the imported `skills/acli/SKILL.md` METHODOLOGY above).
- **Preview before mutate.** Bulk mutations preview via the same `--jql`; creates preview via rendering the payload with `adf2md.py` before firing. This is load-bearing UX, not incidental — replicate it in any new script that writes to Jira/Confluence.
- **acli is the default, Atlassian MCP is the fallback** — the closed gap list is in the imported `skills/acli/SKILL.md` § "When acli can't" above (this exact list drifted stale in this file once already, when it was copied instead of imported). Don't reach for MCP tools outside that list without updating the doc.
- **Content templates are canonical, one per product/type, referenced not duplicated.** Jira templates live in `skills/jira-content/templates/` (Bug/Story/Task/Epic/Sub-task, comments); the Confluence template lives in `skills/confluence-content/templates/`. Acceptance Criteria format/register/coverage rules are the one thing both products share, so they live outside both — `templates/acceptance-criteria.md` at the plugin root; every template file points there instead of restating the rule. If you change the AC rubric, edit it there — this consolidation exists because the old scattered-copies setup let the AC format drift out of sync across 5+ files in practice.
