# jira-acli

An acli-first Jira/Confluence toolkit for Claude Code: bulk work-item ops via JQL,
ADF↔markdown conversion, and guided single-ticket creation with a Thai PO/QA template.

Extracted from [kbg-harness](https://github.com/wasikarn/kbg-harness) — it started as
two skills inside a general engineering harness and moved out here to stand on its own.

## Skills

- **`acli`** — the default path for all Jira/Confluence work: search, view, edit,
  transition, comment, link, clone, bulk ops, Confluence page/space ops, org admin.
  ADF↔markdown conversion scripts included.
- **`create-jira-ticket`** — guided creation of a single Bug or Story using the team's
  Thai PO/QA-readable template, with an acceptance-criteria coaching pass and a
  preview-and-confirm gate before any write. Depends on `acli`'s `md2adf.py` — the two
  skills ship together and are not separable.

## Prerequisites

This plugin is **not self-contained**. It needs, installed separately:

1. **The [`acli` CLI](https://developer.atlassian.com/cloud/acli/)** — installed and
   authenticated (`acli jira auth login` / `acli confluence auth login`). This is the
   primary backend for both skills.
2. **The official Atlassian plugin** (provides the `mcp__plugin_atlassian_atlassian__*`
   MCP tools) — used only as a fallback for the handful of things `acli` genuinely can't
   do yet (see `skills/acli/SKILL.md` § "When acli can't"), and by `create-jira-ticket`
   when `acli` is unavailable or can't set a required field.

Neither skill ships its own `.mcp.json` — bundling one for a fallback path would mean
duplicating credentials and rewriting every MCP tool literal for no functional gain.

## Install

```
/plugin marketplace add wasikarn/jira-acli-plugin
/plugin install jira-acli@wasikarn
```

Ships `defaultEnabled: false` — add `"jira-acli@wasikarn": true` to your Claude Code
`settings.json` after install, then restart.

## Versioning

Bump `version` in **both** `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json`
on every release — same-version edits to a cached plugin are silent no-ops.
