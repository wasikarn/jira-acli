# CLAUDE.md

Map only. What the plugin is, install, and versioning: `README.md`. The acli command reference
loads with the `acli` skill when invoked; do not import it here.

## Commands

No build, package manager, or test suite (a comment in `md2adf.py` mentions `run-tests.sh`; it
does not exist). Local checks:

```bash
python3 -m py_compile skills/*/scripts/*.py
for f in skills/*/scripts/*.sh; do bash -n "$f"; done
python3 skills/acli/scripts/md2adf.py somefile.md | python3 skills/acli/scripts/adf2md.py -   # round-trip
```

## Layout

- `skills/acli` — the mechanical tool (search, view, edit, transition, bulk, Confluence, auth,
  ADF↔Markdown). `skills/jira-content` — Jira templates (Bug/Story/Task/Epic/Sub-task, comments).
  `skills/confluence-content` — Spec/PRD template plus `scripts/inject-mermaid-macros.py`.
- `agents/jira-expert.md`, `agents/confluence-expert.md` — preview-then-stop subagents: they hold
  no MCP tools and never fire a mutating acli command; they return the exact command for the main
  thread to run. Each defers the other product's work to its sibling.
- `templates/acceptance-criteria.md` — the one rule both content skills share; referenced, never
  copied (copies drifted across 5+ files before).
- Scripts: `md2adf.py` (Markdown subset → ADF; nested lists flattened by design, see
  `skills/acli/ISSUES.md` Issue 1), `adf2md.py` (inverse, tolerates acli list-or-dict drift),
  `acli-edit.py` (section-level read-modify-write, since `acli edit --description` replaces the
  body), `acli-ls.py` (normalized search table).

## Rules that came from incidents

- **Routing:** a skill's `description` + `when_to_use` is the routing contract; keep each
  product-specific. A foreign "publish to the tracker" instruction still goes through
  `jira-content`/`confluence-content` for template shape, never straight to acli/MCP (TP-809, TP-806).
- **Fail loud:** scripts exit non-zero with `FATAL:` on unknown field/label/type; never drop and retry.
- **Preview before mutate:** bulk ops preview via the same `--jql`; creates render the payload with
  `adf2md.py` first. Replicate in any new writing script.
- **acli first, Atlassian MCP only for the gaps listed in `skills/acli/SKILL.md` § "When acli
  can't"** (page create/update are MCP-only). Update that list before using MCP elsewhere.
- **Cross-skill coupling:** `jira-content` wraps `acli` scripts via `../../..` climbs; an ADF or
  script-interface change in `acli` must be checked there. New wrappers resolve their dir with
  `BASH_SOURCE[0]`, not `dirname "$0"`.
